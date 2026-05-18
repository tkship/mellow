import 'package:flutter/material.dart';

class ConstellationData {
  final String title;
  final String subTitle;
  final String image;

  final UniqueKey key = UniqueKey();

  ConstellationData(this.title, this.subTitle, this.image);
}
