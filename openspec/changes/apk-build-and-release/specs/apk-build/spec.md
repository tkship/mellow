## ADDED Requirements

### Requirement: Capacitor integration into existing Vite project

The system SHALL integrate Capacitor into the existing React + Vite + TypeScript frontend project, enabling the web application to be packaged as a native Android application.

The integration SHALL include:
- Adding `@capacitor/core` and `@capacitor/cli` as runtime dependencies
- Adding `@capacitor/android` as a runtime dependency
- Creating a `capacitor.config.ts` configuration file at the project root (`frontend/`)
- The `capacitor.config.ts` SHALL configure `appId` as `com.mellow.app`, `appName` as `Mellow`, `webDir` as `dist`, and `server.androidScheme` as `https`

#### Scenario: Capacitor dependencies installed

- **WHEN** running `npm install` in the `frontend/` directory
- **THEN** `@capacitor/core`, `@capacitor/cli`, and `@capacitor/android` SHALL be present in `package.json` dependencies
- **AND** `npx cap` commands SHALL be available

#### Scenario: Capacitor config file created

- **WHEN** Capacitor is initialized
- **THEN** `frontend/capacitor.config.ts` SHALL exist with `appId: 'com.mellow.app'`, `appName: 'Mellow'`, `webDir: 'dist'`, and `server.androidScheme: 'https'`

### Requirement: Configurable API base URL for mobile builds

The system SHALL support a configurable API base URL through environment variables, enabling the mobile APK to connect to a specified backend server instead of relying on Vite's development proxy.

The API client (`frontend/src/api/client.ts`) SHALL use `import.meta.env.VITE_API_BASE_URL` as the base URL when available, falling back to `/api/v1` for development.

A `.env.production` file SHALL be created in `frontend/` with the production backend URL configured as `VITE_API_BASE_URL`.

#### Scenario: Development mode uses proxy

- **WHEN** `VITE_API_BASE_URL` is not set (development)
- **THEN** API requests SHALL use `/api/v1` as the base URL (routed through Vite proxy)

#### Scenario: Production build uses absolute URL

- **WHEN** `VITE_API_BASE_URL` is set (e.g., `https://api.mellow.app`)
- **THEN** API requests SHALL use the configured absolute URL as the base (e.g., `https://api.mellow.app/api/v1`)

#### Scenario: SSE stream URL resolves correctly in WebView

- **WHEN** running inside a Capacitor Android WebView
- **AND** `VITE_API_BASE_URL` is set to a production server
- **THEN** SSE streaming URLs SHALL resolve to the production server URL, not the local WebView URL

### Requirement: Android platform initialization and configuration

The system SHALL initialize a Capacitor Android platform project within the `frontend/` directory and configure it with appropriate application metadata.

The Android project SHALL have:
- `versionCode` set to `1` and `versionName` set to `0.1.0`
- `package` name set to `com.mellow.app`
- Application name displayed as `Mellow`
- `minSdkVersion` set to `24` (Android 7.0)
- `targetSdkVersion` set to `34` (Android 14)

#### Scenario: Android project generated

- **WHEN** running `npx cap add android` in the `frontend/` directory
- **THEN** an `android/` directory SHALL be created with a complete Gradle-based Android project
- **AND** `AndroidManifest.xml` SHALL declare `package="com.mellow.app"`

#### Scenario: Version information set

- **WHEN** building the v0.1 APK
- **THEN** the Android project SHALL have `versionCode="1"` and `versionName="0.1.0"`

### Requirement: Build and sign APK

The system SHALL provide a build process that generates a debug-signed APK file from the Vite-built web assets packaged through Capacitor.

The build process SHALL:
1. Run `npm run build` to produce static assets in `frontend/dist/`
2. Run `npx cap sync android` to copy web assets into the Android project
3. Run Gradle assembleDebug to produce the APK
4. Output the APK file at `frontend/android/app/build/outputs/apk/debug/app-debug.apk`

#### Scenario: Successful Vite build

- **WHEN** running `npm run build` in `frontend/`
- **THEN** static assets SHALL be produced in `frontend/dist/`
- **AND** `index.html` SHALL exist in `frontend/dist/`

#### Scenario: Capacitor sync copies web assets

- **WHEN** running `npx cap sync android` after a successful Vite build
- **THEN** web assets from `frontend/dist/` SHALL be copied to `frontend/android/app/src/main/assets/public/`
- **AND** Capacitor configuration SHALL be synchronized to the Android project

#### Scenario: APK build produces output file

- **WHEN** running Gradle assembleDebug in the Android project
- **THEN** an APK file SHALL be produced at `frontend/android/app/build/outputs/apk/debug/app-debug.apk`
- **AND** the APK SHALL be installable on Android devices running API level 24+

### Requirement: Upload APK to GitHub Releases

The system SHALL upload the generated APK file to a GitHub Release on the `tkship/mellow` repository with tag `v0.1`.

The release SHALL:
- Have title `v0.1 - First Android APK`
- Include the APK artifact as a downloadable asset
- Include release notes describing this as the first Android build

#### Scenario: GitHub Release created with APK

- **WHEN** the APK build is complete
- **AND** a GitHub release is created with tag `v0.1`
- **THEN** the APK file SHALL be uploaded as a release asset
- **AND** users SHALL be able to download and install the APK from the release page

#### Scenario: Release tag does not already exist

- **WHEN** creating a GitHub release for `v0.1`
- **AND** no existing tag `v0.1` exists on the repository
- **THEN** the release SHALL be created with a new `v0.1` tag pointing to the current commit