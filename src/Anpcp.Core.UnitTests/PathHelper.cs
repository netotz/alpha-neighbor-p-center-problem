using System.Runtime.CompilerServices;

namespace Anpcp.Core.UnitTests;

public static class PathHelper
{
    public static string GetAbsolute(string filePath, [CallerFilePath] string currentPath = "")
    {
        var currentDirectory = Path.GetDirectoryName(currentPath) ?? "";

        return Path.Combine(currentDirectory, filePath);
    }
}
