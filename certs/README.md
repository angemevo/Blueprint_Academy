# Certificats racine d'entreprise (optionnel)

Placer ici les certificats racine (`*.crt`, format PEM) de votre proxy
d'inspection TLS (Zscaler, Netskope, Bluecoat...). Ils sont installes dans le
magasin de confiance des images Docker au moment du build, sinon `pip` et `npm`
echouent derriere un proxy qui dechiffre le trafic.

Le dossier peut rester vide : le build fonctionne sans.

Les fichiers `*.crt` sont ignores par git (specifiques a chaque poste).

## Export depuis Windows

```powershell
$c = Get-ChildItem Cert:\LocalMachine\Root | Where-Object { $_.Subject -match 'Zscaler' } | Select-Object -First 1
$b64 = [System.Convert]::ToBase64String($c.RawData, 'InsertLineBreaks')
"-----BEGIN CERTIFICATE-----`n$b64`n-----END CERTIFICATE-----" | Set-Content certs\zscaler-root-ca.crt -Encoding ascii
```

## Export depuis macOS / Linux

```bash
# depuis le trousseau ou le fichier fourni par votre IT
cp /chemin/vers/proxy-root-ca.pem certs/proxy-root-ca.crt
```
