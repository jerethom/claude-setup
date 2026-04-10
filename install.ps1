# install.ps1 - Windows installer for Claude Setup
$ErrorActionPreference = "Stop"

$REPO_URL = "https://github.com/jerethom/claude-setup"
$REPO_NAME = "claude-setup"
$TEMP_DIR = Join-Path $env:TEMP "claude-setup-install-$(Get-Random)"

try {
    Write-Host "Installation du setup Claude..." -ForegroundColor Cyan

    # Install mise if not present
    if (-not (Get-Command mise -ErrorAction SilentlyContinue)) {
        Write-Host "Installation de mise..." -ForegroundColor Yellow
        if (Get-Command winget -ErrorAction SilentlyContinue) {
            winget install jdx.mise --accept-package-agreements --accept-source-agreements
        } elseif (Get-Command scoop -ErrorAction SilentlyContinue) {
            scoop install mise
        } else {
            Write-Host "Erreur: winget ou scoop requis pour installer mise." -ForegroundColor Red
            Write-Host "Installe scoop: irm get.scoop.sh | iex" -ForegroundColor Yellow
            exit 1
        }
        # Refresh PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
        Write-Host "mise installe" -ForegroundColor Green
    } else {
        Write-Host "mise deja installe" -ForegroundColor Green
    }

    # Clone repo to temp directory
    Write-Host "Telechargement de la configuration..." -ForegroundColor Cyan
    git clone --depth 1 $REPO_URL "$TEMP_DIR\$REPO_NAME" 2>$null

    # Copy .claude directory
    Write-Host "Copie de la configuration .claude..." -ForegroundColor Cyan
    if (Test-Path .claude) {
        Remove-Item -Recurse -Force .claude
        Write-Host "   (ancienne configuration remplacee)"
    }
    Copy-Item -Recurse -Force "$TEMP_DIR\$REPO_NAME\.claude" .\.claude

    # Merge mise.toml with markers
    Write-Host "Copie des fichiers de configuration..." -ForegroundColor Cyan
    $MISE_MARKER_START = "# >>> Claude Setup >>>"
    $MISE_MARKER_END = "# <<< Claude Setup <<<"
    $MISE_SRC = "$TEMP_DIR\$REPO_NAME\.claude\config\mise.toml"
    $MISE_SRC_CONTENT = Get-Content -Path $MISE_SRC -Raw -Encoding UTF8

    if (-not (Test-Path mise.toml)) {
        Copy-Item $MISE_SRC .\mise.toml
    } elseif ((Get-Content mise.toml -Raw -Encoding UTF8) -match [regex]::Escape($MISE_MARKER_START)) {
        # Remove old section between markers
        $content = Get-Content mise.toml -Raw -Encoding UTF8
        $pattern = "(?s)" + [regex]::Escape($MISE_MARKER_START) + ".*?" + [regex]::Escape($MISE_MARKER_END) + "\r?\n?"
        $content = $content -replace $pattern, ""
        $content = $content.TrimEnd() + "`n" + $MISE_SRC_CONTENT
        Set-Content -Path mise.toml -Value $content -NoNewline -Encoding UTF8
        Write-Host "   (section Claude Setup mise a jour dans mise.toml)"
    } else {
        Add-Content -Path mise.toml -Value "`n$MISE_SRC_CONTENT" -Encoding UTF8
        Write-Host "   (section Claude Setup ajoutee a mise.toml)"
    }

    # Copy other config files
    Copy-Item "$TEMP_DIR\$REPO_NAME\.claude\config\mcp.docker-compose.yml" .\mcp.docker-compose.yml -Force
    Copy-Item "$TEMP_DIR\$REPO_NAME\.claude\config\.cgcignore" .\.cgcignore -Force
    Copy-Item "$TEMP_DIR\$REPO_NAME\.claude\config\.mcp.json" .\.mcp.json -Force

    # Adapt .mcp.json for Windows (demongrep path)
    $mcpContent = Get-Content .\.mcp.json -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($mcpContent.mcpServers.demongrep) {
        $demongrep_bin = Join-Path $env:LOCALAPPDATA "claude-setup\demongrep\target\release\demongrep.exe"
        $mcpContent.mcpServers.demongrep.command = "cmd"
        $mcpContent.mcpServers.demongrep.args = @("/c", "$demongrep_bin mcp .")
        $mcpContent | ConvertTo-Json -Depth 10 | Set-Content .\.mcp.json -Encoding UTF8
    }

    # Update .gitignore
    Write-Host "Mise a jour du .gitignore..." -ForegroundColor Cyan
    $GI_MARKER_START = "# >>> Claude Setup - CGC ignore >>>"
    $GI_MARKER_END = "# <<< Claude Setup - CGC ignore <<<"

    if (Test-Path .gitignore) {
        $giContent = Get-Content .gitignore -Raw -Encoding UTF8
        if ($giContent -match [regex]::Escape($GI_MARKER_START)) {
            $pattern = "(?s)" + [regex]::Escape($GI_MARKER_START) + ".*?" + [regex]::Escape($GI_MARKER_END) + "\r?\n?"
            $giContent = $giContent -replace $pattern, ""
            Set-Content -Path .gitignore -Value $giContent -NoNewline -Encoding UTF8
            Write-Host "   (ancienne section remplacee)"
        }
    } else {
        New-Item -ItemType File -Path .gitignore | Out-Null
    }

    $cgcIgnoreContent = Get-Content "$TEMP_DIR\$REPO_NAME\.claude\config\.cgcignore" -Raw -Encoding UTF8
    $section = "`n$GI_MARKER_START`n$cgcIgnoreContent"
    if (-not $section.EndsWith("`n")) { $section += "`n" }
    $section += "$GI_MARKER_END`n"
    Add-Content -Path .gitignore -Value $section -NoNewline -Encoding UTF8

    # Run mise setup
    Write-Host "Lancement de mise setup..." -ForegroundColor Cyan
    mise run setup

    Write-Host ""
    Write-Host "Installation terminee !" -ForegroundColor Green
    Write-Host ""
    Write-Host "Pour demarrer les serveurs MCP, lance : mise run mcps"
    Write-Host "Pour demarrer Docker (Neo4j) : mise run docker"

} finally {
    # Cleanup temp directory
    if (Test-Path $TEMP_DIR) {
        Remove-Item -Recurse -Force $TEMP_DIR -ErrorAction SilentlyContinue
    }
}
