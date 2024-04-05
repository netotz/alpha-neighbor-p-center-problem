namespace Anpcp.Experiments;

public static class AppSettings
{
    public static string AnpcpRepoPath { get; set; } = "";
    public static string TspLibPath => Path.Combine(AnpcpRepoPath, "data", "tsplib");
    public static string OutPath => Path.Combine(AnpcpRepoPath, "out");
}
