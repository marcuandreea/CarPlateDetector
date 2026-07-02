"""Database package exposing DB helper functions grouped by module."""
from .masini import (
    enter_parking,
    pay_parking,
    get_parking_fee,
    leave_parking,
    get_parking_status_by_plate,
    show_masini,
    delete_masina,
    count_cars_in_parking,
)
from .taxe import (
    update_taxa,
    add_taxa,
    delete_taxa,
    show_taxe,
)
from .subscriptions import (
    fetch_subscription_plans,
    create_subscription_plan,
    update_subscription_plan,
    delete_subscription_plan,
)
from .user_subscriptions import (
    fetch_user_subscriptions,
    delete_user_subscription,
    activate_subscription,
    fetch_active_subscription_plan_by_plate,
    fetch_active_subscription_by_user_id,
)
from .users import (
    ensure_users_table_exists,
    fetch_user_by_email,
    fetch_user_by_id,
    fetch_user_by_plate,
    insert_user,
    update_user,
    update_user_qr_path,
    fetch_users_for_admin,
    delete_user_by_id,
)

__all__ = [
    'enter_parking',
    'pay_parking',
    'get_parking_fee',
    'leave_parking',
    'get_parking_status_by_plate',
    'update_taxa',
    'show_masini',
    'show_taxe',
    'count_cars_in_parking',
    'add_taxa',
    'delete_taxa',
    'delete_masina',
    'fetch_subscription_plans',
    'create_subscription_plan',
    'update_subscription_plan',
    'delete_subscription_plan',
    'fetch_user_subscriptions',
    'delete_user_subscription',
    'ensure_users_table_exists',
    'fetch_user_by_email',
    'fetch_user_by_id',
    'fetch_user_by_plate',
    'insert_user',
    'update_user',
    'update_user_qr_path',
    'fetch_users_for_admin',
    'delete_user_by_id',
    'activate_subscription',
    'fetch_active_subscription_plan_by_plate',
    'fetch_active_subscription_by_user_id',
]
