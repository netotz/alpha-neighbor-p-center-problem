using System.Diagnostics;

namespace Anpcp.Experiments.Grasp;

internal class GraspResult
{
    internal required string NameWithExtension { get; init; }
    private string Name => NameWithExtension.Split('.')[0];
    internal string SplitName => Name[..^2];
    internal int Index => int.Parse(Name.Split('_')[^1]);

    internal required int PValue { get; init; }
    internal required int Alpha { get; init; }

    internal int BestRgdOfv { get; set; } = int.MaxValue;
    internal int BestAfvsOfv { get; set; } = int.MaxValue;
    internal double BestOfvsDiff => 100 * Math.Abs(BestAfvsOfv - BestRgdOfv) / (double)BestRgdOfv;

    internal double AfvsMinImprovement { get; set; } = double.MaxValue;
    internal double AfvsMaxImprovement { get; set; } = double.MinValue;
    internal List<double> AfvsImprovements { get; set; } = [];
    internal double AfvsAvgImprovement => AfvsImprovements.Average();

    internal int LastImprovedIteration { get; set; } = -1;

    internal Stopwatch Stopwatch { get; set; } = new();
}
