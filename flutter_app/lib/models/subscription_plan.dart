class SubscriptionPlan {
  final int id;
  final String nume;
  final double price;
  final int duration;

  const SubscriptionPlan({
    required this.id,
    required this.nume,
    required this.price,
    required this.duration,
  });

  // Factory constructor pentru a crea un SubscriptionPlan dintr-un JSON
  factory SubscriptionPlan.fromJson(Map<String, dynamic> json) {
    return SubscriptionPlan(
      id: (json['id'] as num?)?.toInt() ?? 0,
      nume: json['nume']?.toString() ?? '',
      price: (json['price'] as num?)?.toDouble() ?? 0.0,
      duration: (json['duration'] as num?)?.toInt() ?? 0,
    );
  }
}
