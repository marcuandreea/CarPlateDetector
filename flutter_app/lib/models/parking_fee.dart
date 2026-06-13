class ParkingFee {
  final String parkingCode;
  final int parkedMinutes;
  final int billableMinutes;
  final double amount;
  final String currency;

  const ParkingFee({
    required this.parkingCode,
    required this.parkedMinutes,
    required this.billableMinutes,
    required this.amount,
    required this.currency,
  });

  factory ParkingFee.fromJson(Map<String, dynamic> json) {
    return ParkingFee(
      parkingCode: json['parking_code']?.toString() ?? '',
      parkedMinutes: (json['parked_minutes'] as num?)?.toInt() ?? 0,
      billableMinutes: (json['billable_minutes'] as num?)?.toInt() ?? 0,
      amount: (json['amount'] as num?)?.toDouble() ?? 0,
      currency: json['currency']?.toString() ?? 'RON',
    );
  }
}
