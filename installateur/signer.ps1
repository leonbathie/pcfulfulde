# ============================================================
#  Signe un fichier (exe, dll) du Clavier Pulaar
# ============================================================
#  Une signature reconnue par les autres PC demande un certificat de signature
#  de code delivre a votre nom par une autorite (Certum, SSL.com, Sectigo...).
#  Le certificat est cherche :
#   - dans un fichier .pfx : CLAVIER_PULAAR_PFX (chemin) et
#     CLAVIER_PULAAR_PFX_MDP (mot de passe) ;
#   - sinon dans le magasin de Windows (Cert:\CurrentUser\My), par son
#     empreinte : CLAVIER_PULAAR_CERTIFICAT. Les certificats sur carte ou
#     « cloud » (Certum SimplySign, SSL.com eSigner) y apparaissent.
#  L'horodatage garde la signature valide apres l'expiration du certificat.
param([Parameter(Mandatory = $true)][string]$Fichier)

$ErrorActionPreference = 'Stop'
if ($env:CLAVIER_PULAAR_PFX) {
    $certificat = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2(
        $env:CLAVIER_PULAAR_PFX, $env:CLAVIER_PULAAR_PFX_MDP)
} elseif ($env:CLAVIER_PULAAR_CERTIFICAT) {
    $certificat = Get-ChildItem Cert:\CurrentUser\My -CodeSigningCert |
        Where-Object { $_.Thumbprint -eq $env:CLAVIER_PULAAR_CERTIFICAT } | Select-Object -First 1
} else {
    throw 'Aucun certificat : definissez CLAVIER_PULAAR_PFX (et CLAVIER_PULAAR_PFX_MDP) ou CLAVIER_PULAAR_CERTIFICAT.'
}
if (-not $certificat) { throw 'Certificat de signature de code introuvable.' }

$horodatage = if ($env:CLAVIER_PULAAR_HORODATAGE) { $env:CLAVIER_PULAAR_HORODATAGE } else { 'http://timestamp.digicert.com' }
Set-AuthenticodeSignature -FilePath $Fichier -Certificate $certificat -HashAlgorithm SHA256 `
    -TimestampServer $horodatage | Out-Null

# La signature doit etre la notre, meme si le certificat n'est pas encore reconnu ici.
$signature = Get-AuthenticodeSignature -FilePath $Fichier
if (-not $signature.SignerCertificate -or $signature.SignerCertificate.Thumbprint -ne $certificat.Thumbprint) {
    throw "Signature absente sur $Fichier : $($signature.StatusMessage)"
}
Write-Host "Signe : $Fichier ($($signature.Status))"
