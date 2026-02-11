class GeoCoordinate {
  final double lat;
  final double lng;

  GeoCoordinate({required this.lat, required this.lng});

  factory GeoCoordinate.fromJson(Map<String, dynamic> json) {
    return GeoCoordinate(
      lat: (json['lat'] as num).toDouble(),
      lng: (json['lng'] as num).toDouble(),
    );
  }

  Map<String, dynamic> toJson() => {'lat': lat, 'lng': lng};
}

class POI {
  final String name;
  final String description;
  final GeoCoordinate geoCoordinate;
  final String poiType; // "restaurant", "lodge", "tourist_destination", "unknown"
  final List<String> imageUrls;
  final String? openingHours;
  final String? address;
  final String? specialInstructions;
  final String cost;

  POI({
    required this.name,
    required this.description,
    required this.geoCoordinate,
    required this.poiType,
    required this.imageUrls,
    this.openingHours,
    this.address,
    this.specialInstructions,
    this.cost = '',
  });

  factory POI.fromJson(Map<String, dynamic> json) {
    final geoCoord = json['geo_coordinate'] as Map<String, dynamic>;
    final images = json['images'] as Map<String, dynamic>?;
    final urls = (images?['urls'] as List<dynamic>?)?.cast<String>() ?? [];

    return POI(
      name: json['name'] as String,
      description: json['description'] as String,
      geoCoordinate: GeoCoordinate.fromJson(geoCoord),
      poiType: json['poi_type'] as String? ?? 'unknown',
      imageUrls: urls,
      openingHours: json['opening_hours'] as String?,
      address: json['address'] as String?,
      specialInstructions: json['special_instructions'] as String?,
      cost: json['cost'] as String? ?? '',
    );
  }

  Map<String, dynamic> toJson() => {
        'name': name,
        'description': description,
        'geo_coordinate': geoCoordinate.toJson(),
        'poi_type': poiType,
        'images': {'urls': imageUrls},
        if (openingHours != null) 'opening_hours': openingHours,
        if (address != null) 'address': address,
        if (specialInstructions != null)
          'special_instructions': specialInstructions,
        'cost': cost,
      };
}
