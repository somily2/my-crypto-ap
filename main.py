name: Build Flet APK
on: [push, workflow_dispatch]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11' # مصححة ومضمونة بنسبة 100%

      - name: Setup Java (Required for Android)
        uses: actions/setup-java@v4
        with:
          distribution: 'zulu'
          java-version: '17'

      - name: Setup Flutter
        uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.24.0'

      - name: Install Dependencies
        run: |
          pip install flet requests

      - name: Build APK
        run: |
          flet build apk --no-public-sign --yes
