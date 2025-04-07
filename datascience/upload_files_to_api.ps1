$url = "http://127.0.0.1:5000/predict/sarimax"
$file1 = "C:\Users\elise\Documents\datascience\conso_mix_RTE_2023.xls"
$file2 = "C:\Users\elise\Documents\datascience\conso_mix_RTE_2024.xls"

function Upload-File {
    param (
        [string]$FilePath,
        [string]$Url
    )
    
    try {
        # Méthode plus simple avec -InFile
        $response = Invoke-RestMethod -Uri $Url -Method Post `
            -InFile $FilePath `
            -ContentType "application/vnd.ms-excel"
        
        return $response
    }
    catch {
        Write-Output "Erreur lors de l'upload: $($_.Exception.Message)"
        
        # Détails supplémentaires si disponible
        if ($_.Exception.Response) {
            $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
            $reader.BaseStream.Position = 0
            $reader.DiscardBufferedData()
            $errorDetails = $reader.ReadToEnd()
            Write-Output "Détails de l'erreur: $errorDetails"
        }
        
        return $null
    }
}

# Vérification préalable des fichiers
if (-not (Test-Path $file1)) { Write-Error "Fichier $file1 introuvable"; exit }
if (-not (Test-Path $file2)) { Write-Error "Fichier $file2 introuvable"; exit }

# Upload
Write-Output "Tentative de connexion au serveur..."
try {
    $testConnection = Invoke-RestMethod -Uri "http://127.0.0.1:5000" -Method Get -TimeoutSec 3
    Write-Output "Serveur détecté: $($testConnection.message)"
}
catch {
    Write-Error "Échec de connexion au serveur. Vérifiez que:"
    Write-Error "1. Le serveur Flask est en cours d'exécution"
    Write-Error "2. Le port 5000 n'est pas bloqué par le pare-feu"
    exit
}

Write-Output "Envoi du fichier 1..."
$response1 = Upload-File -FilePath $file1 -Url $url

Write-Output "Envoi du fichier 2..."
$response2 = Upload-File -FilePath $file2 -Url $url

# Affichage des résultats
Write-Output "`nRésultat pour conso_mix_RTE_2023.xls :"
if ($response1) { $response1 | ConvertTo-Json -Depth 5 } else { "Aucune réponse valide" }

Write-Output "`nRésultat pour conso_mix_RTE_2024.xls :"
if ($response2) { $response2 | ConvertTo-Json -Depth 5 } else { "Aucune réponse valide" }