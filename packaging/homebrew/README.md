# Homebrew packaging

`gpg-gui.rb` is the formula published in the tap repo `lac3/homebrew-tap` (as `Formula/gpg-gui.rb`).

## One-time setup

1. Create a public GitHub repo named `homebrew-tap` under `lac3`.
2. Copy `gpg-gui.rb` into it as `Formula/gpg-gui.rb`.

## Releasing a new version

```bash
# in this repo
git tag v1.1.0 && git push origin v1.1.0
curl -sL https://github.com/lac3/gpg_gui/archive/refs/tags/v1.1.0.tar.gz | shasum -a 256
```

In the tap's `Formula/gpg-gui.rb`, update `url` (tag) and `sha256`, then commit and push.

## Testing locally before publishing

```bash
brew install --build-from-source ./packaging/homebrew/gpg-gui.rb   # needs a real tag + sha256
brew install --HEAD ./packaging/homebrew/gpg-gui.rb                # builds from main instead
brew test gpg-gui
brew audit --strict gpg-gui
```

Recent Homebrew versions refuse to install formulae from a bare file path. If that happens, put the
formula in a local tap first:

```bash
brew tap-new lac3/local
cp packaging/homebrew/gpg-gui.rb "$(brew --repository lac3/local)/Formula/"
brew install --HEAD lac3/local/gpg-gui
```
