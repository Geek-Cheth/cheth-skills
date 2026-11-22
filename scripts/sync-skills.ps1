#Requires -Version 5.1
<#
.SYNOPSIS
  Idempotently junction-link every skill in this repo into Cursor, Codex,
  Claude Code / .agents, and Antigravity (standalone + T3 Code instances).

.NOTES
  - No admin required (New-Item -ItemType Junction).
  - Never touches real user folders, .system, skills-cursor, or builtin paths.
  - Safe to re-run: existing junctions/symlinks at the same target are removed
    and recreated; real directories at the destination are refused.
#>
[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$SkillsRoot = Join-Path $RepoRoot 'skills'
$PluginName = 'cheth-skills'

# Paths we must never remove or overwrite
$ProtectedNameFragments = @(
    '\.system\',
    '\skills-cursor\',
    '\builtin\',
    '\.system/',
    '/skills-cursor/',
    '/builtin/'
)

function Test-IsProtectedPath {
    param([string]$Path)
    $norm = $Path.Replace('/', '\')
    foreach ($frag in $ProtectedNameFragments) {
        $fragNorm = $frag.Replace('/', '\')
        if ($norm -like "*$fragNorm*") { return $true }
    }
    # Also refuse known protected skill names if they somehow appear as dest leaf
    $leaf = Split-Path -Leaf $norm
    if ($leaf -in @('.system', 'skills-cursor', 'builtin')) { return $true }
    return $false
}

function Test-IsReparsePoint {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) { return $false }
    $item = Get-Item -LiteralPath $Path -Force
    return [bool]($item.Attributes -band [IO.FileAttributes]::ReparsePoint)
}

function Remove-ExistingJunctionSafely {
    param(
        [Parameter(Mandatory)][string]$TargetPath
    )
    if (-not (Test-Path -LiteralPath $TargetPath)) {
        return 'absent'
    }
    if (Test-IsProtectedPath -Path $TargetPath) {
        throw "Refusing to touch protected path: $TargetPath"
    }
    if (Test-IsReparsePoint -Path $TargetPath) {
        # Remove junction/symlink only — does not delete the link target contents
        cmd /c "rmdir `"$TargetPath`"" | Out-Null
        if (Test-Path -LiteralPath $TargetPath) {
            throw "Failed to remove existing junction/symlink: $TargetPath"
        }
        return 'removed-junction'
    }
    # Real file or directory — never delete user content
    throw "Destination exists and is not a junction/symlink (refusing to overwrite): $TargetPath"
}

function Ensure-ParentDirectory {
    param([Parameter(Mandatory)][string]$Path)
    $parent = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }
}

function New-SkillJunction {
    param(
        [Parameter(Mandatory)][string]$SourcePath,
        [Parameter(Mandatory)][string]$DestPath,
        [Parameter(Mandatory)][string]$Label
    )
    $result = [ordered]@{
        Label   = $Label
        Dest    = $DestPath
        Source  = $SourcePath
        Status  = 'unknown'
        Detail  = ''
    }

    try {
        if (Test-IsProtectedPath -Path $DestPath) {
            throw "Protected destination refused: $DestPath"
        }
        Ensure-ParentDirectory -Path $DestPath
        $prior = Remove-ExistingJunctionSafely -TargetPath $DestPath
        New-Item -ItemType Junction -Path $DestPath -Target $SourcePath | Out-Null
        if ($prior -eq 'removed-junction') {
            $result.Status = 'updated'
            $result.Detail = 'replaced existing junction'
        }
        else {
            $result.Status = 'created'
            $result.Detail = 'new junction'
        }
    }
    catch {
        $result.Status = 'error'
        $result.Detail = $_.Exception.Message
    }

    return [pscustomobject]$result
}

# --- Discover skills ---------------------------------------------------------
if (-not (Test-Path -LiteralPath $SkillsRoot)) {
    Write-Error "Skills root not found: $SkillsRoot"
    exit 1
}

$skills = @(Get-ChildItem -LiteralPath $SkillsRoot -Directory -ErrorAction Stop |
    Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName 'SKILL.md') } |
    Sort-Object Name)

if (-not $skills) {
    Write-Warning "No skill folders with SKILL.md found under $SkillsRoot"
}

$results = New-Object System.Collections.Generic.List[object]

Write-Host ""
Write-Host "cheth-skills sync"
Write-Host "  RepoRoot : $RepoRoot"
Write-Host "  Skills   : $($skills.Count) discovered"
Write-Host ""

# --- Per-skill agent skill destinations --------------------------------------
$skillDestRoots = @(
    @{ Label = 'Cursor'; Root = (Join-Path $env:USERPROFILE '.cursor\skills') }
    @{ Label = 'Codex';  Root = (Join-Path $env:USERPROFILE '.codex\skills') }
    @{ Label = '.agents'; Root = (Join-Path $env:USERPROFILE '.agents\skills') }
    @{ Label = 'Claude';  Root = (Join-Path $env:USERPROFILE '.claude\skills') }
)

foreach ($skill in $skills) {
    $skillName = $skill.Name
    $skillSrc  = $skill.FullName

    # Hard refuse linking protected / reserved skill names
    if ($skillName -in @('.system', 'skills-cursor', 'builtin')) {
        $results.Add([pscustomobject]@{
            Label  = 'SKIP'
            Dest   = $skillName
            Source = $skillSrc
            Status = 'skipped'
            Detail = 'reserved/protected skill name'
        })
        continue
    }

    foreach ($destRoot in $skillDestRoots) {
        $dest = Join-Path $destRoot.Root $skillName
        $results.Add(
            (New-SkillJunction -SourcePath $skillSrc -DestPath $dest -Label "$($destRoot.Label)/$skillName")
        )
    }
}

# --- Antigravity plugin (whole repo) -----------------------------------------
$antigravityDestinations = New-Object System.Collections.Generic.List[string]

$standaloneAg = Join-Path $env:USERPROFILE '.gemini\config\plugins'
$antigravityDestinations.Add((Join-Path $standaloneAg $PluginName))

$t3AgProviders = Join-Path $env:USERPROFILE '.t3\userdata\providers\antigravity'
if (Test-Path -LiteralPath $t3AgProviders) {
    Get-ChildItem -LiteralPath $t3AgProviders -Directory -ErrorAction SilentlyContinue | ForEach-Object {
        $pluginDir = Join-Path $_.FullName 'config\plugins'
        $antigravityDestinations.Add((Join-Path $pluginDir $PluginName))
    }
}

foreach ($agDest in $antigravityDestinations) {
    $label = if ($agDest -like '*\.t3\*') {
        $instance = ($agDest -replace [regex]::Escape((Join-Path $env:USERPROFILE '.t3\userdata\providers\antigravity\')), '') -replace '\\config\\plugins\\cheth-skills$', ''
        "Antigravity-T3/$instance"
    }
    else {
        'Antigravity'
    }
    $results.Add(
        (New-SkillJunction -SourcePath $RepoRoot -DestPath $agDest -Label $label)
    )
}

# --- Summary table -----------------------------------------------------------
Write-Host ""
Write-Host ("{0,-36} {1,-10} {2}" -f 'Target', 'Status', 'Detail')
Write-Host ("{0,-36} {1,-10} {2}" -f ('-' * 36), ('-' * 10), ('-' * 40))

$ok = 0
$err = 0
foreach ($r in $results) {
    Write-Host ("{0,-36} {1,-10} {2}" -f $r.Label, $r.Status, $r.Detail)
    if ($r.Status -in @('created', 'updated')) { $ok++ }
    elseif ($r.Status -eq 'error') { $err++ }
}

Write-Host ""
Write-Host "Done: $ok linked/updated, $err errors (of $($results.Count) total)."
if ($err -gt 0) { exit 1 }
exit 0
