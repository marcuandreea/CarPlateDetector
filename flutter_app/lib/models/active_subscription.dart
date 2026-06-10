class ActiveSubscription {
  final int id;
  final int userId;
  final DateTime startDate;
  final DateTime endDate;
  final int planId;
  final bool active;
  final String planNume;
  final double planPrice;
  final int planDuration;

  const ActiveSubscription({
    required this.id,
    required this.userId,
    required this.startDate,
    required this.endDate,
    required this.planId,
    required this.active,
    required this.planNume,
    required this.planPrice,
    required this.planDuration,
  });

  factory ActiveSubscription.fromJson(Map<String, dynamic> json) {
    return ActiveSubscription(
      id: (json['id'] as num?)?.toInt() ?? 0,
      userId: (json['user_id'] as num?)?.toInt() ?? 0,
      startDate: DateTime.parse(json['start_date']?.toString() ?? ''),
      endDate: DateTime.parse(json['end_date']?.toString() ?? ''),
      planId: (json['plan_id'] as num?)?.toInt() ?? 0,
      active: json['active'] == true,
      planNume: json['plan_nume']?.toString() ?? '',
      planPrice: (json['plan_price'] as num?)?.toDouble() ?? 0.0,
      planDuration: (json['plan_duration'] as num?)?.toInt() ?? 0,
    );
  }
}
