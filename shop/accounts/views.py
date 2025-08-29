from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from decimal import Decimal
from .models import Profile
from django.db.models import Sum
from expenses.models import Expense
from income.models import Income  # adjust import if Income is elsewhere
from datetime import date
from django.utils import timezone
from django.db.models.functions import TruncMonth
import datetime as dt
from django.db import transaction
from .models import Transaction


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None :
            login(request, user)
            request.session['greeting_shown'] = False  # reset for each login
            return redirect('greeting')  # instead of dashboard

        else:
            messages.error(request, "Invalid username or password.")
    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


def register_view(request):
    if request.method == 'POST':
        username = request.POST['username'].strip()
        email = request.POST['email'].strip()
        password = request.POST['password']
        confirm = request.POST['confirm_password']
        role = request.POST.get('role', 'staff')
        avatar = request.FILES.get('avatar')

        if avatar and avatar.size > 1024 * 1024:
            messages.error(request, "Avatar must be 1 MB or less.")
            return redirect('register')

        if password != confirm:
            messages.error(request, "Passwords do not match.")
            return redirect('register')
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register')

        with transaction.atomic():
            user = User.objects.create_user(username=username, email=email, password=password)
            # signal created profile; update it:
            profile = getattr(user, 'profile', None)
            if profile is None:
                profile = Profile.objects.create(user=user, role=role, avatar=avatar)
            else:
                profile.role = role
                if avatar:
                    profile.avatar = avatar
                profile.save()

        messages.success(request, "Account created")
        return redirect('login')
    return render(request, 'register.html')


def upload_avatar(request):
    if request.method == "POST":
        avatar = request.FILES.get("avatar")
        if avatar:
            profile = Profile.objects.get(user=request.user)
            profile.avatar = avatar
            profile.save()
            return redirect("profile")  # change 'profile' to your URL name
    return render(request, "upload_avatar.html")


def forgot_password_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        if User.objects.filter(email=email).exists():
            # send reset email (dummy example)
            send_mail(
                "Password Reset Request",
                "Click the link below to reset your password.",
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            messages.success(request, "Password reset email sent!")
        else:
            messages.error(request, "Email not found!")
    return render(request, "forgot_password.html")


# Try import Income model if you have one; otherwise ignore
try:
    from income.models import Income

    HAVE_INCOME = True
except Exception:
    HAVE_INCOME = False


@login_required
def dashboard(request):
    user = request.user
    profile = getattr(user, "profile", None)
    role = getattr(profile, "role", "staff") if profile else "staff"

    # ---------- incomes & expenses queryset (role-based) ----------
    if role == "owner":
        incomes_qs = Income.objects.all()
        expenses_qs = Expense.objects.all()
        transactions_qs = Transaction.objects.all()
    else:
        incomes_qs = Income.objects.filter(user=user)
        expenses_qs = Expense.objects.filter(user=user)
        transactions_qs = Transaction.objects.filter(user=user)

    # ---------- totals ----------
    income_agg = incomes_qs.aggregate(total=Sum("amount"))["total"] or 0
    expense_agg = expenses_qs.aggregate(total=Sum("amount"))["total"] or 0

    total_income = Decimal(income_agg)
    total_expense = Decimal(expense_agg)
    balance = total_income - total_expense

    # transactions count
    tx_count = incomes_qs.count() + expenses_qs.count()

    # ---------- recent transactions (last 5) ----------
    recent_items = []
    for e in expenses_qs.order_by("-date")[:10]:
        recent_items.append({
            "id": e.id,
            "date": e.date,
            "description": e.description,
            "amount": float(e.amount),
            "type": "expense",
            "timestamp": e.date.isoformat() if e.date else ""
        })
    for i in incomes_qs.order_by("-date")[:10]:
        recent_items.append({
            "id": i.id,
            "date": i.date,
            "description": i.description,
            "amount": float(i.amount),
            "type": "income",
            "timestamp": i.date.isoformat() if i.date else ""
        })
    recent_sorted = sorted(recent_items, key=lambda x: x["timestamp"], reverse=True)[:5]

    # ---------- monthly chart data (last 6 months) ----------
    months_count = 6
    today = timezone.localdate()
    start_idx = today.year * 12 + today.month - 1 - (months_count - 1)
    months = []
    for j in range(months_count):
        idx = start_idx + j
        y = idx // 12
        m = idx % 12 + 1
        months.append(date(y, m, 1))
    start_date = months[0]

    # income per month
    inc_map = {}
    for r in (incomes_qs.filter(date__gte=start_date)
              .annotate(month=TruncMonth("date"))
              .values("month")
              .annotate(total=Sum("amount"))
              .order_by("month")):
        mon = r["month"].date() if hasattr(r["month"], "date") else r["month"]
        inc_map[(mon.year, mon.month)] = float(r["total"] or 0)

    # expense per month
    exp_map = {}
    for r in (expenses_qs.filter(date__gte=start_date)
              .annotate(month=TruncMonth("date"))
              .values("month")
              .annotate(total=Sum("amount"))
              .order_by("month")):
        mon = r["month"].date() if hasattr(r["month"], "date") else r["month"]
        exp_map[(mon.year, mon.month)] = float(r["total"] or 0)

    labels = [m.strftime("%b %Y") for m in months]
    income_values = [inc_map.get((m.year, m.month), 0) for m in months]
    expense_values = [exp_map.get((m.year, m.month), 0) for m in months]

    # ---------- mode charts ----------
    income_mode_labels, income_mode_values = [], []
    for r in incomes_qs.values("mode").annotate(total=Sum("amount")).order_by("-total"):
        income_mode_labels.append(r["mode"] or "Unknown")
        income_mode_values.append(float(r["total"] or 0))

    expense_mode_labels, expense_mode_values = [], []
    for r in expenses_qs.values("mode").annotate(total=Sum("amount")).order_by("-total"):
        expense_mode_labels.append(r["mode"] or "Unknown")
        expense_mode_values.append(float(r["total"] or 0))

    # ---------- final context ----------
    context = {
        "total_income": float(total_income),
        "total_expense": float(total_expense),
        "transactions_count": tx_count,
        "balance": float(balance),
        "recent_transactions": recent_sorted,
        "month_labels": labels,
        "income_values": income_values,
        "expense_values": expense_values,
        "income_mode_labels": income_mode_labels,
        "income_mode_values": income_mode_values,
        "expense_mode_labels": expense_mode_labels,
        "expense_mode_values": expense_mode_values,
        "is_owner": role == "owner",
        "role": role, 
    }

    return render(request, "dashboard.html", context)



@login_required
def greeting_view(request):
    # If greeting is already shown, skip directly to dashboard
    if request.session.get("greeting_shown"):
        return redirect("dashboard")

    request.session["greeting_shown"] = True  # mark as shown
    return render(request, "greeting.html")

    context = {
        "profile": profile,
        # 'total_income': total_income,
        # 'total_expense': total_expense,
        # 'balance': balance,
    }
    return render(request, "dashboard.html", context)


def about_view(request):
    return render(request, "about.html")


def expenses_view(request):
    return render(request, "expenses.html")


@login_required
def owner_dashboard(request):
    incomes = Income.objects.all().order_by("-date")
    expenses = Expense.objects.all().order_by("-date")
    return render(request, "dashboards/owner_dashboard.html",{
        "incomes": incomes,
        "expenses": expenses,
    })



@login_required
def staff_dashboard(request):
    incomes = Income.objects.filter(user=request.user).order_by('-date')
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    context = {'incomes': incomes, 'expenses': expenses}
    return render(request, "dashboards/staff_dashboard.html",{
        "incomes": incomes,
        "expenses": expenses,
    })


@login_required
def activity_view(request):
    # safe access to profile and role
    profile = getattr(request.user, "profile", None)
    role = getattr(profile, "role", "staff") if profile else "staff"

    if role == "owner":
        incomes = Income.objects.select_related("user").all().order_by("-date")
        expenses = Expense.objects.select_related("user").all().order_by("-date")
        is_owner = True
    else:
        incomes = Income.objects.filter(user=request.user).order_by("-date")
        expenses = Expense.objects.filter(user=request.user).order_by("-date")
        is_owner = False

    return render(request, "dashboards/activity.html", {
        "incomes": incomes,
        "expenses": expenses,
        "is_owner": is_owner,
    })

@login_required
def dashboard_redirect(request):
    role = getattr(getattr(request.user, "profile", None), "role", "staff")
    if role == "owner":
        return redirect("owner_dashboard")
    return redirect("staff_dashboard")

