import 'poi_model.dart';

class Transportation {
  final String? duration;
  final String? method;
  final double? cost;

  Transportation({
    this.duration,
    this.method,
    this.cost,
  });

  factory Transportation.fromJson(Map<String, dynamic> json) {
    return Transportation(
      duration: json['duration'] as String?,
      method: json['method'] as String?,
      cost: (json['cost'] as num?)?.toDouble(),
    );
  }

  Map<String, dynamic> toJson() => {
        if (duration != null) 'duration': duration,
        if (method != null) 'method': method,
        if (cost != null) 'cost': cost,
      };
}

class Block {
  final String time;
  final String description;
  final List<POI>? pois;
  final Transportation? transportation;

  Block({
    required this.time,
    required this.description,
    this.pois,
    this.transportation,
  });

  factory Block.fromJson(Map<String, dynamic> json) {
    final poisJson = json['pois'] as List<dynamic>?;
    final transportJson = json['transportation'] as Map<String, dynamic>?;

    return Block(
      time: json['time'] as String,
      description: json['description'] as String,
      pois: poisJson
          ?.map((p) => POI.fromJson(p as Map<String, dynamic>))
          .toList(),
      transportation:
          transportJson != null ? Transportation.fromJson(transportJson) : null,
    );
  }

  Map<String, dynamic> toJson() => {
        'time': time,
        'description': description,
        if (pois != null) 'pois': pois!.map((p) => p.toJson()).toList(),
        if (transportation != null) 'transportation': transportation!.toJson(),
      };
}

class Day {
  final String highlight;
  final String? lodging;
  final List<Block> blocks;

  Day({
    required this.highlight,
    this.lodging,
    required this.blocks,
  });

  factory Day.fromJson(Map<String, dynamic> json) {
    final blocksJson = json['blocks'] as List<dynamic>;
    return Day(
      highlight: json['highlight'] as String,
      lodging: json['lodging'] as String?,
      blocks: blocksJson
          .map((b) => Block.fromJson(b as Map<String, dynamic>))
          .toList(),
    );
  }

  Map<String, dynamic> toJson() => {
        'highlight': highlight,
        if (lodging != null) 'lodging': lodging,
        'blocks': blocks.map((b) => b.toJson()).toList(),
      };
}

class PlanOption {
  final String overallCost;
  final String generalNotes;
  final List<Day> days;

  PlanOption({
    required this.overallCost,
    required this.generalNotes,
    required this.days,
  });

  factory PlanOption.fromJson(Map<String, dynamic> json) {
    final daysJson = json['days'] as List<dynamic>;
    return PlanOption(
      overallCost: json['overall_cost'] as String,
      generalNotes: json['general_notes'] as String,
      days: daysJson.map((d) => Day.fromJson(d as Map<String, dynamic>)).toList(),
    );
  }

  Map<String, dynamic> toJson() => {
        'overall_cost': overallCost,
        'general_notes': generalNotes,
        'days': days.map((d) => d.toJson()).toList(),
      };
}
