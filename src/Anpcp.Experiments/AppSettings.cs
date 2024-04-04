namespace Anpcp.Experiments;

public record AppPaths(string TspLib, string Out)
{
    public AppPaths() : this("", "") { }
}

public static class AppSettings
{
    public static AppPaths AppPaths { get; set; } = new();
}
