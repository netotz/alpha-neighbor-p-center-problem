dotnet publish .\src\Anpcp.Experiments\ -r win-x64 -c Release

Push-Location
cd .\src\Anpcp.Experiments\bin\Release\net9.0\win-x64\publish\

# set environment variable for repository path in terminal session
# $env:AnpcpRepoPath = "path\to\repo\alpha-neighbor-p-center-problem"

.\Anpcp.Experiments.exe

Pop-Location
