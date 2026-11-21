class GpgGui < Formula
  desc "Simple graphical interface for GPG file encryption and decryption"
  homepage "https://github.com/lac3/gpg_gui"
  url "https://github.com/lac3/gpg_gui/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "REPLACE_WITH_SHA256_OF_TARBALL"
  head "https://github.com/lac3/gpg_gui.git", branch: "main"

  depends_on :macos
  depends_on "gnupg"
  depends_on "python-tk@3.13" # also pulls in python@3.13

  def python
    Formula["python@3.13"].opt_bin/"python3.13"
  end

  def install
    libexec.install Dir["*.py"], "GpgGui.icns", "GpgGui.png"

    # Terminal command: gpg-gui
    (bin/"gpg-gui").write <<~SH
      #!/bin/bash
      export PATH="#{HOMEBREW_PREFIX}/bin:$PATH"
      exec "#{python}" "#{libexec}/gpg_gui.py" "$@"
    SH
    chmod 0755, bin/"gpg-gui"

    # Minimal .app bundle so the app can be launched from Finder, the Dock or Spotlight.
    # It is built locally by Homebrew, so it is not quarantined by Gatekeeper.
    contents = prefix/"GPG GUI.app/Contents"
    (contents/"MacOS").mkpath
    (contents/"Resources").install_symlink libexec/"GpgGui.icns"
    (contents/"MacOS/GpgGui").write <<~SH
      #!/bin/bash
      exec "#{opt_bin}/gpg-gui"
    SH
    chmod 0755, contents/"MacOS/GpgGui"
    (contents/"Info.plist").write <<~XML
      <?xml version="1.0" encoding="UTF-8"?>
      <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
      <plist version="1.0">
      <dict>
        <key>CFBundleName</key><string>GPG GUI</string>
        <key>CFBundleDisplayName</key><string>GPG GUI</string>
        <key>CFBundleExecutable</key><string>GpgGui</string>
        <key>CFBundleIdentifier</key><string>com.gpggui.app</string>
        <key>CFBundleIconFile</key><string>GpgGui.icns</string>
        <key>CFBundlePackageType</key><string>APPL</string>
        <key>CFBundleShortVersionString</key><string>#{version}</string>
        <key>CFBundleVersion</key><string>#{version}</string>
        <key>LSMinimumSystemVersion</key><string>11.0</string>
        <key>NSHighResolutionCapable</key><true/>
      </dict>
      </plist>
    XML
  end

  def caveats
    <<~EOS
      To add GPG GUI to your Applications folder:
        ln -sf "#{opt_prefix}/GPG GUI.app" /Applications/

      You can also start it from Terminal with:
        gpg-gui
    EOS
  end

  test do
    system python, "-c", "import tkinter"
    system python, "-c", "import sys; sys.path.insert(0, '#{libexec}'); import gpg_process, preferences"
    assert_path_exists prefix/"GPG GUI.app/Contents/MacOS/GpgGui"
  end
end
