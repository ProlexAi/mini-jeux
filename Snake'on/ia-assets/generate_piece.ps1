# Generate one isolated game asset piece (head / tail / body tile / decoration)
# via a local ComfyUI instance (SDXL + IPAdapter style-reference conditioning).
#
# Prerequisite: ComfyUI running locally, see PIPELINE-ASSETS-IA.md in this folder
# for setup, known pitfalls, and the full recipe this script encodes.
#
# Usage example:
#   .\generate_piece.ps1 -RefImage "ref_body.png" -Prompt "snake head, side view, closed mouth, calm expression, matching material and color of the reference" -FilenamePrefix "skin_ice_head"

param(
    [string]$ComfyUrl = "http://127.0.0.1:8188",
    [string]$Checkpoint = "sd_xl_base_1.0.safetensors",
    [Parameter(Mandatory=$true)][string]$RefImage,
    [Parameter(Mandatory=$true)][string]$Prompt,
    [string]$NegativePrompt = "blurry, low quality, text, watermark, multiple heads, extra limbs, deformed",
    [string]$FilenamePrefix = "snakeon_asset",
    [double]$IpAdapterWeight = 1.0,
    [string]$IpAdapterWeightType = "style transfer",
    [string]$IpAdapterPreset = "PLUS (high strength)",
    [string]$LoraName = "",
    [double]$LoraStrength = 0.8,
    [int]$Width = 1024,
    [int]$Height = 1024,
    [int]$Steps = 25,
    [double]$Cfg = 6.0,
    [string]$SamplerName = "dpmpp_2m",
    [string]$Scheduler = "karras",
    [int]$Seed = 123,
    [int]$MaxWaitSeconds = 900
)

$ErrorActionPreference = "Stop"

# Known-good range: IpAdapterWeight above ~1.2 with "strong style transfer" can
# destabilize the generation into saturated noise. See PIPELINE-ASSETS-IA.md pitfall 4.

# LoRA optionnelle (style vectoriel/plat) : si -LoraName est fourni, le modele et le CLIP
# passent par LoraLoader (node "11") avant IPAdapter/CLIPTextEncode ; sinon ils sortent
# directement du checkpoint (node "1"), comportement inchange.
$modelSource = if ($LoraName) { @("11", 0) } else { @("1", 0) }
$clipSource = if ($LoraName) { @("11", 1) } else { @("1", 1) }

$workflow = @{
    "1" = @{
        class_type = "CheckpointLoaderSimple"
        inputs = @{ ckpt_name = $Checkpoint }
    }
    "2" = @{
        class_type = "LoadImage"
        inputs = @{ image = $RefImage }
    }
    "3" = @{
        class_type = "IPAdapterUnifiedLoader"
        inputs = @{
            model = $modelSource
            preset = $IpAdapterPreset
        }
    }
    "4" = @{
        class_type = "IPAdapterAdvanced"
        inputs = @{
            model = @("3", 0)
            ipadapter = @("3", 1)
            image = @("2", 0)
            weight = $IpAdapterWeight
            weight_type = $IpAdapterWeightType
            combine_embeds = "concat"
            start_at = 0.0
            end_at = 1.0
            embeds_scaling = "V only"
        }
    }
    "5" = @{
        class_type = "CLIPTextEncode"
        inputs = @{ text = $Prompt; clip = $clipSource }
    }
    "6" = @{
        class_type = "CLIPTextEncode"
        inputs = @{ text = $NegativePrompt; clip = $clipSource }
    }
    "7" = @{
        class_type = "EmptyLatentImage"
        inputs = @{ width = $Width; height = $Height; batch_size = 1 }
    }
    "8" = @{
        class_type = "KSampler"
        inputs = @{
            model = @("4", 0)
            positive = @("5", 0)
            negative = @("6", 0)
            latent_image = @("7", 0)
            seed = $Seed
            steps = $Steps
            cfg = $Cfg
            sampler_name = $SamplerName
            scheduler = $Scheduler
            denoise = 1.0
        }
    }
    "9" = @{
        class_type = "VAEDecode"
        inputs = @{ samples = @("8", 0); vae = @("1", 2) }
    }
    "10" = @{
        class_type = "SaveImage"
        inputs = @{ images = @("9", 0); filename_prefix = $FilenamePrefix }
    }
}

if ($LoraName) {
    $workflow["11"] = @{
        class_type = "LoraLoader"
        inputs = @{
            model = @("1", 0)
            clip = @("1", 1)
            lora_name = $LoraName
            strength_model = $LoraStrength
            strength_clip = $LoraStrength
        }
    }
}

$body = @{ prompt = $workflow; client_id = "snakeon-asset-gen" } | ConvertTo-Json -Depth 10

$sw = [System.Diagnostics.Stopwatch]::StartNew()
$submit = Invoke-RestMethod -Uri "$ComfyUrl/prompt" -Method Post -Body $body -ContentType "application/json"
$promptId = $submit.prompt_id
Write-Output "Submitted, prompt_id=$promptId"

$done = $false
while (-not $done -and $sw.Elapsed.TotalSeconds -lt $MaxWaitSeconds) {
    Start-Sleep -Seconds 5
    try {
        $hist = Invoke-RestMethod -Uri "$ComfyUrl/history/$promptId" -Method Get
        if ($hist.$promptId) { $done = $true }
    } catch {}
}
$sw.Stop()

if ($done) {
    Write-Output "Done in $([math]::Round($sw.Elapsed.TotalSeconds,1)) s"
    $hist.$promptId.outputs | ConvertTo-Json -Depth 10
} else {
    Write-Output "Timeout after $MaxWaitSeconds s, no result"
}
