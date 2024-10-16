using Anpcp.Core.Heuristics.Constructives;
using Anpcp.Core.Instances;
using Anpcp.Core.Solutions;
using Anpcp.Interactive.Pdp.Models;

using ScottPlot;

namespace Anpcp.Interactive.Pdp;

/// <summary>
/// Interactive version of <see cref="FgdConstructive"/> to generate visualizations.
/// </summary>
public class FgdInteractive
    : IConstructive<InstanceSameSet, PdpSolution>
{
    public int PSize { get; }
    public InstanceSameSet Instance { get; }
    public int? Seed { get; }
    private Random Random { get; }
    public Dictionary<int, ClosestCenter> DistancesMemory { get; }
    public PdpSolution Solution { get; }
    public int LastInserted { get; set; }
    /// <summary>
    /// Current objective function value x(S).
    /// </summary>
    public int CurrentOfv { get; set; } = int.MaxValue;
    private Queue<int> ClosedFacilitiesQueue { get; set; }
    public PlotConfig PlotConfig { get; set; } = new();

    public FgdInteractive(int pSize, InstanceSameSet instance, int? seed)
    {
        PSize = pSize;
        Instance = instance;
        Seed = seed;
        Random = Seed is null
            ? new Random()
            : new Random(Seed.Value);

        // memory dictionary of minimum distances to S
        // O(m)
        DistancesMemory = Enumerable
            .Repeat(int.MaxValue, Instance.Facilities.Length)
            .Select((v, i) => new
            {
                Key = i,
                Value = new ClosestCenter(v)
            })
            .ToDictionary(
                s => s.Key,
                s => s.Value);

        Solution = new PdpSolution(Instance.FacilitiesIndices.ToHashSet());

        Start();
        HurryForMemory();
    }

    private void Start()
    {
        // start with random center
        LastInserted = Random.GetItems(
            Solution.ClosedFacilities.ToArray(), 1)[0];

        Solution.Insert(LastInserted);
        DistancesMemory.Remove(LastInserted);

        ResetClosedFacilitiesQueue();
    }

    public void ResetClosedFacilitiesQueue()
    {
        ClosedFacilitiesQueue = new Queue<int>(Solution.ClosedFacilities);
    }

    /// <summary>
    /// Tries to do an iteration of the main `while` loop of the algorithm.
    /// </summary>
    /// <returns>`false` if |S| = p or memory isn't fully updated</returns>
    public bool TryIterateMain()
    {
        // S already has p centers
        if (Solution.OpenFacilities.Count == PSize)
        {
            return false;
        }

        // if memory isn't fully updated
        if (ClosedFacilitiesQueue.Count > 0)
        {
            return false;
        }

        // get farthest facility to S
        // O(m - p) ~= O(m)
        LastInserted = DistancesMemory
            .MaxBy(p => p.Value.Distance)
            .Key;

        Solution.Insert(LastInserted);

        // update x(S)
        CurrentOfv = Math.Min(
            CurrentOfv,
            DistancesMemory[LastInserted].Distance);

        DistancesMemory.Remove(LastInserted);

        ResetClosedFacilitiesQueue();

        return true;
    }

    /// <summary>
    /// Tries to plot an iteration of the `for` loop that updates the memory.
    /// </summary>
    /// <returns>`null` if memory is completely updated.</returns>
    public Plot? TryPlotForMemoryIteration(bool isHurrying = false)
    {
        // if empty
        if (!ClosedFacilitiesQueue.TryDequeue(out var fi))
        {
            return null;
        }

        var closestCenter = DistancesMemory[fi];
        var liDistance = Instance.DistancesFF[fi, LastInserted];
        var minDistance = Math.Min(closestCenter.Distance, liDistance);

        // only update if necessary (li < cc)
        if (minDistance == liDistance)
        {
            DistancesMemory[fi] = new(minDistance, LastInserted);
        }

        if (isHurrying)
        {
            return null;
        }

        var plot = new Plot
        {
            ScaleFactor = PlotConfig.ScaleFactor
        };

        // closed facilities
        var cfVertices = Instance.Facilities
            .Where(f => Solution.ClosedFacilities.Contains(f.Index));
        plot.Add.ScatterPoints(
            cfVertices.Select(v => (double)v.XCoord).ToArray(),
            cfVertices.Select(v => (double)v.YCoord).ToArray(),
            new(PlotConfig.CfColor));

        // centers
        var sVertices = Instance.Facilities
            .Where(f => Solution.OpenFacilities.Contains(f.Index)
                && f.Index != LastInserted);
        plot.Add.ScatterPoints(
            sVertices.Select(v => (double)v.XCoord).ToArray(),
            sVertices.Select(v => (double)v.YCoord).ToArray(),
            new(PlotConfig.SColor));

        var fiVertex = Instance.Facilities[fi];
        plot.Add.ScatterPoints(
            (double[])[fiVertex.XCoord],
            (double[])[fiVertex.YCoord],
            new(PlotConfig.FiColor));

        var liVertex = Instance.Facilities[LastInserted];
        plot.Add.ScatterPoints(
            (double[])[liVertex.XCoord],
            (double[])[liVertex.YCoord],
            new(PlotConfig.LiColor));

        var ccVertex = Instance.Facilities[closestCenter.Index];
        plot.Add.ScatterPoints(
            (double[])[ccVertex.XCoord],
            (double[])[ccVertex.YCoord],
            new(PlotConfig.CcColor));

        return plot;
    }

    /// <summary>
    /// Runs all iterations left to fully update memory.
    /// </summary>
    public void HurryForMemory()
    {
        while (ClosedFacilitiesQueue.Count > 0)
        {
            TryPlotForMemoryIteration(true);
        }
    }

    /// <summary>
    /// Do not call, throws exception.
    /// It must be here because of the interface contract.
    /// </summary>
    public PdpSolution Construct()
    {
        throw new NotImplementedException();
    }
}