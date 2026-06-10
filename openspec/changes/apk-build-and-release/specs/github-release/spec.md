## ADDED Requirements

### Requirement: GitHub Release distribution workflow

The system SHALL provide a documented, repeatable workflow for creating a GitHub Release with an APK artifact on the `tkship/mellow` repository.

The workflow SHALL:
1. Create a git tag `v0.1` at the current commit
2. Push the tag to the remote repository
3. Create a GitHub Release associated with the tag
4. Upload the built APK as a release asset
5. Include release notes describing the v0.1 release

The release notes SHALL mention:
- This is the first Android APK build
- The app is for testing purposes
- Users need to enable "Install from unknown sources" on their Android device

#### Scenario: Create and publish release

- **WHEN** running the release workflow after a successful APK build
- **THEN** a GitHub Release SHALL exist at `https://github.com/tkship/mellow/releases/tag/v0.1`
- **AND** the release page SHALL have a downloadable APK file
- **AND** release notes SHALL describe the v0.1 first Android build

#### Scenario: APK file size is reasonable

- **WHEN** the APK is built
- **THEN** the file size SHALL be under 50MB (typical for a Capacitor WebView app without large assets)