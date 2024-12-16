using Anpcp.Core.Heuristics.Constructives.Rgd;
using Anpcp.Core.Heuristics.LocalSearches.Afvs;
using Anpcp.Core.Instances;
using Anpcp.Core.Solutions;

using Microsoft.Data.Analysis;

namespace Anpcp.Experiments.Grasp;

internal static class GraspExperiment
{
    private static string OutFolder => "grasp";
    private static int VariationsAmount => 10;
    private static string[] TspFileNames { get; } = new[]
    {
        "pr439_293_146",
        //"rat575_384_191",
        //"rat783_522_261",
        //"dsj1000_667_333",
        //"rl1323_882_441",
        //"rl1889_1260_629"
    }
        .SelectMany(
            _ => Enumerable.Range(0, VariationsAmount),
            (n, i) => $"{n}_{i}.anpcp.tsp")
        .ToArray();
    private static int Seed => 20241201;
    private static double[] PFractions { get; } = [0.05, 0.1, 0.15];
    private static int[] AlphaValues { get; } = [2, 3];

    internal static InstanceTwoSets[] Instances { get; private set; } = [];
    internal static List<GraspResult> Results { get; private set; } = [];

    internal static void Run()
    {
        Instances = Util.ReadTspFilesTwoSets(TspFileNames);

        Console.WriteLine("Running GRASP experiment...");

        foreach (var instance in Instances)
        {
            Console.WriteLine($"\nSolving instance: {instance.Name}...");

            foreach (var pFrac in PFractions)
            {
                var p = (int)(instance.Facilities.Length * pFrac);

                Console.WriteLine($"\n\tUsing p={p}...");

                foreach (var alpha in AlphaValues)
                {
                    Console.WriteLine($"\t\tUsing alpha={alpha}...");

                    var rgd = new RandomizedGreedyDispersion<InstanceTwoSets>(instance, p, 0.2f, Seed);

                    var solution = new AnpcpSolution(instance.FacilityIds.ToHashSet());
                    var afvs = new AlphaFastVertexSubstitution(instance, p, alpha, solution, Seed);

                    var grasp = new GraspRgdAfvs_Result(100, TimeSpan.FromSeconds(1800), rgd, afvs);

                    Console.WriteLine("\n\t\tRunning GRASP...");

                    grasp.Run();

                    Results.Add(grasp.Result);
                }
            }
        }
    }

    internal static void SaveCsvResults()
    {
        var nameColumn = DataFrameColumn.Create(
            "name",
            Results.Select(r => r.InstanceName));

        var indexColumn = DataFrameColumn.Create(
            "index",
            Results.Select(r => r.Index));

        var pColumn = DataFrameColumn.Create(
            "p",
            Results.Select(r => r.PValue));

        var alphaColumn = DataFrameColumn.Create(
            "alpha",
            Results.Select(r => r.Alpha));

        var bestRgdOfvColumn = DataFrameColumn.Create(
            "best_rgd_ofv",
            Results.Select(r => r.BestRgdOfv));

        var bestAfvsOfvColumn = DataFrameColumn.Create(
            "best_afvs_ofv",
            Results.Select(r => r.BestAfvsOfv));

        var bestOfvsDiffColumn = DataFrameColumn.Create(
            "best_ofvs_diff",
            Results.Select(r => r.BestOfvsDiff));

        var afvsMinImprovementColumn = DataFrameColumn.Create(
            "afvs_min_improvement",
            Results.Select(r => r.AfvsMinImprovement));

        var afvsMaxImprovementColumn = DataFrameColumn.Create(
            "afvs_max_improvement",
            Results.Select(r => r.AfvsMaxImprovement));

        var afvsAvgImprovementColumn = DataFrameColumn.Create(
            "afvs_avg_improvement",
            Results.Select(r => r.AfvsAvgImprovement));

        var lastImprovedIterationColumn = DataFrameColumn.Create(
            "last_improved_iteration",
            Results.Select(r => r.LastImprovedIteration));

        var timeColumn = DataFrameColumn.Create(
            "time_s",
            Results.Select(r => r.Stopwatch.Elapsed.Seconds));

        var dataFrame = new DataFrame(
            nameColumn,
            indexColumn,
            pColumn,
            alphaColumn,
            bestRgdOfvColumn,
            bestAfvsOfvColumn,
            bestOfvsDiffColumn,
            afvsMinImprovementColumn,
            afvsMaxImprovementColumn,
            afvsAvgImprovementColumn,
            lastImprovedIterationColumn,
            timeColumn
        );

        var csvPath = Path.Combine(AppSettings.OutPath, OutFolder, "grasp1.csv");

        DataFrame.SaveCsv(dataFrame, csvPath);
    }
}
