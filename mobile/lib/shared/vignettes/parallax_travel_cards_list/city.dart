import 'package:flutter/material.dart';

/// Data model for a travel destination city used by parallax travel card components.
class City {
  final String name;
  final String title;
  final String description;
  final Color color;

  const City({
    required this.title,
    required this.name,
    required this.description,
    required this.color,
  });
}
