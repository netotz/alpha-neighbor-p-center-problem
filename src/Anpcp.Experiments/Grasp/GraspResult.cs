using System.Diagnostics;

namespace Anpcp.Experiments.Grasp;

internal class GraspResult
{
    internal required string FullName { get; init; }
    internal string InstanceName => FullName.Split('.')[0];
    internal int Index => FullName[^1];
    internal required int PValue { get; init; }
    internal required int Alpha { get; init; }
    internal int BestRgdOfv { get; set; } = int.MaxValue;
    internal int BestAfvsOfv { get; set; } = int.MaxValue;
    internal double BestOfvsDiff => 100 * Math.Abs(BestAfvsOfv - BestRgdOfv) / BestRgdOfv;
    internal double AfvsMinImprovement { get; set; } = int.MaxValue;
    internal double AfvsMaxImprovement { get; set; } = int.MinValue;
    internal List<double> AfvsImprovements { get; set; } = [];
    internal double AfvsAvgImprovement => AfvsImprovements.Average();
    internal int LastImprovedIteration { get; set; } = -1;
    internal Stopwatch Stopwatch { get; set; } = new();
}
