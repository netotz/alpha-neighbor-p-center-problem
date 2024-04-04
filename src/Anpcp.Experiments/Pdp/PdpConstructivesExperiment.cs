using System.Diagnostics;

using Anpcp.Core.Heuristics.Constructives;
using Anpcp.Core.Instances;
using Anpcp.Core.Solutions;

using Microsoft.Data.Analysis;

namespace Anpcp.Experiments.Pdp;

public class PdpConstructivesExperiment
{
    private static string OutFolder => "pdp";
    private static string[] TspFileNames { get; } = [
        "dsj1000.tsp",
        "fl3795.tsp",
        "rl5934.tsp",
        "pla7397.tsp",
        "usa13509.tsp",
    ];
    private static int Seed => 20240403;
    private static double[] PFractions { get; } = [0.05, 0.1, 0.2];

    public IEnumerable<InstanceSameSet> Instances { get; } = TspFileNames
            .Select(n => new InstanceSameSet(GetTspFilePath(n)));
    /// <summary>
    /// Results of Original Greedy Dispersion (OGD).
    /// </summary>
    public List<PdpResult<OgdConstructive>> OgdResults { get; private set; } = [];
    /// <summary>
    /// Results of Fast Greedy Dispersion (FGD).
    /// </summary>
    public List<PdpResult<FgdConstructive>> FgdResults { get; private set; } = [];

    public void Run()
    {
        foreach (var instance in Instances)
        {
            foreach (var pFrac in PFractions)
            {
                var p = (int)(instance.Facilities.Length * pFrac);

                var fgd = new FgdConstructive(instance, p, Seed);

                var stopwatch = Stopwatch.StartNew();
                // O(mp)
                var fgdSolution = fgd.Construct();
                stopwatch.Stop();

                // no need to update x(S) ;)

                FgdResults.Add(new(instance.Name, fgd, fgdSolution, stopwatch.Elapsed));

                var ogd = new OgdConstructive(instance, p, Seed);

                stopwatch = Stopwatch.StartNew();
                // O(mp**2)
                var ogdSolution = ogd.Construct();
                stopwatch.Stop();

                var ofvStopwatch = Stopwatch.StartNew();
                // O(p**2)
                ogdSolution.UpdateObjectiveFunctionValue(instance.DistancesFF);
                ofvStopwatch.Stop();

                OgdResults.Add(new(instance.Name, ogd, ogdSolution, stopwatch.Elapsed, ofvStopwatch.Elapsed));
            }
        }
    }

    public void WriteCsvResults()
    {
        var ogdColumns = GetCommonColumns(OgdResults);
        var ofvTime = DataFrameColumn.Create(
            "ofv time",
            OgdResults.Select(r => r.ObjectiveFunctionTime?.ToString("s\\.FFF")));
        var ogdDataFrame = new DataFrame([.. ogdColumns, ofvTime]);

        var fgdColumns = GetCommonColumns(FgdResults);
        var fasterColumn = DataFrameColumn.Create(
            "faster x",
            FgdResults
                .Zip(OgdResults, (fgd, ogd) => (fgd, ogd))
                .Select(z => z.ogd.HeuristicTime / z.fgd.HeuristicTime));
        var fgdDataFrame = new DataFrame([.. fgdColumns, fasterColumn]);

        var bothDataFrame = ogdDataFrame.Join(fgdDataFrame, " ogd", " rgd");

        // columns are not numbers
        // TODO: find way to format column
        //bothDataFrame["faster x"] = bothDataFrame["time ogd"] / bothDataFrame["time rgd"];

        var instancesColumn = DataFrameColumn.Create(
            "instance",
            FgdResults.Select(r => r.InstanceName));
        var pColumn = DataFrameColumn.Create(
            "p",
            FgdResults.Select(r => r.Constructive.PSize));

        bothDataFrame.Columns.Insert(0, pColumn);
        bothDataFrame.Columns.Insert(0, instancesColumn);

        var csvPath = Path.Combine(AppSettings.AppPaths.Out, OutFolder, "both1.csv");

        DataFrame.SaveCsv(bothDataFrame, csvPath);
    }

    private static DataFrameColumn[] GetCommonColumns<TConstructive>(List<PdpResult<TConstructive>> results)
        where TConstructive : IConstructive<InstanceSameSet, PdpSolution>
    {
        var ofvColumn = DataFrameColumn.Create(
            "x(S)",
            results.Select(r => r.Solution.ObjectiveFunctionValue));
        var timeColumn = DataFrameColumn.Create(
            "time",
            results.Select(r => r.HeuristicTime.ToString("s\\.FFF")));

        return [ofvColumn, timeColumn];
    }

    private static string GetTspFilePath(string tspFileName)
    {
        return Path.Combine(AppSettings.AppPaths.TspLib, tspFileName);
    }
}
