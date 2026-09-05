# Generate an asset piece via Flux.1-schnell (GGUF quantized) - text-only,
# no IPAdapter yet. Validates Flux runs correctly on this DirectML machine
# before layering ComfyUI-IPAdapter-Flux on top.
#
# Prerequisite: ComfyUI running locally with ComfyUI-GGUF custom node
# installed, and flux1-schnell-Q6_K.gguf / clip_l / t5xxl_fp8_e4m3fn / ae.safetensors
# downloaded. See PIPELINE-ASSETS-IA.md.

param(
    [string]$ComfyUrl = "http://127.0.0.1:8188",
    [string]$UnetName = "flux1-schnell-Q6_K.gguf",
    [Parameter(Mandatory=$true)][string]$Prompt,
    [string]$FilenamePrefix = "snakeon_flux_test",
    [int]$Width = 1024,
    [int]$Height = 1024,
    [int]$Steps = 4,
    [double]$Guidance = 3.5,
    [int]$Seed = 123,
    [int]$MaxWaitSeconds = 900
)

$ErrorActionPreference = "Stop"

$workflow = @{
    "1" = @{
        class_type = "UnetLoaderGGUF"
        inputs = @{ unet_name = $UnetName }
    }
    "2" = @{
        class_type = "DualCLIPLoader"
        inputs = @{
            clip_name1 = "t5xxl_fp8_e4m3fn.safetensors"
            clip_name2 = "clip_l.safetensors"
            type = "flux"
        }
    }
    "3" = @{
        class_type = "VAELoader"
        inputs = @{ vae_name = "ae.safetensors" }
    }
    "4" = @{
        class_type = "CLIPTextEncode"
        inputs = @{ text = $Prompt; clip = @("2", 0) }
    }
    "5" = @{
        class_type = "FluxGuidance"
        inputs = @{ conditioning = @("4", 0); guidance = $Guidance }
    }
    "6" = @{
        class_type = "ConditioningZeroOut"
        inputs = @{ conditioning = @("4", 0) }
    }
    "7" = @{
        class_type = "EmptySD3LatentImage"
        inputs = @{ width = $Width; height = $Height; batch_size = 1 }
    }
    "8" = @{
        class_type = "KSampler"
        inputs = @{
            model = @("1", 0)
            positive = @("5", 0)
            negative = @("6", 0)
            latent_image = @("7", 0)
            seed = $Seed
            steps = $Steps
            cfg = 1.0
            sampler_name = "euler"
            scheduler = "simple"
            denoise = 1.0
        }
    }
    "9" = @{
        class_type = "VAEDecode"
        inputs = @{ samples = @("8", 0); vae = @("3", 0) }
    }
    "10" = @{
        class_type = "SaveImage"
        inputs = @{ images = @("9", 0); filename_prefix = $FilenamePrefix }
    }
}

$body = @{ prompt = $workflow; client_id = "snakeon-flux-test" } | ConvertTo-Json -Depth 10

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
