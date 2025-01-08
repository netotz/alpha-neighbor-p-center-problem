using Anpcp.Core.Instances;

namespace Anpcp.Experiments;

public static class Util
{
    public static InstanceSameSet[] ReadTspFilesSameSet(string[] tspFileNames)
    {
        Console.WriteLine("Reading TSPLIB files...");

        var instances = tspFileNames
            .Select(n => new InstanceSameSet(GetTspFilePath(n)))
            .ToArray();

        Console.WriteLine("Done." + Environment.NewLine);

        return instances;
    }

    public static InstanceTwoSets[] ReadTspFilesTwoSets(string[] tspFileNames)
    {
        Console.WriteLine("Reading TSPLIB files...");

        var instances = tspFileNames
            .Select(n => new InstanceTwoSets(GetTspFilePath(n)))
            .ToArray();

        Console.WriteLine("Done." + Environment.NewLine);

        return instances;
    }

    private static string GetTspFilePath(string tspFileName)
    {
        return Path.Combine(AppSettings.TspLibPath, tspFileName);
    }
}
