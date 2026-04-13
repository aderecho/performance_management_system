from django.utils.timezone import now
from datetime import timedelta
from django.contrib.auth import get_user_model

User = get_user_model()


class UserDashboardService:

    @staticmethod
    def get_stats():
        today = now()

        # Start of current month (e.g., Jan 1, 00:00:00)
        start_current_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Compute previous month range
        last_month_end = start_current_month - timedelta(seconds=1)
        start_last_month = last_month_end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Total users
        total_current = User.objects.count()

        # Total users before current month
        total_last = User.objects.filter(created_at__lt=start_current_month).count()

        # Total active users
        active_current = User.objects.filter(is_active=True).count()

        # Total active users before current month
        active_last = User.objects.filter(
            is_active=True,
            updated_at__lt=start_current_month
        ).count()

        # Total new users
        new_current = User.objects.filter(
            created_at__gte=start_current_month
        ).count()

        # Total new users before current month
        new_last = User.objects.filter(
            created_at__gte=start_last_month,
            created_at__lt=start_current_month
        ).count()

        return {
            "total_users": UserDashboardService.build_metric(total_current, total_last),
            "active_users": UserDashboardService.build_metric(active_current, active_last),
            "new_users": UserDashboardService.build_metric(new_current, new_last),
        }


    def build_metric(current, previous):
        if previous == 0:
            trend = 100 if current > 0 else 0
        else:
            trend = ((current - previous) / previous) * 100

        return {
            "value": current,
            "previous": previous,
            "trend": round(trend, 2)
        }