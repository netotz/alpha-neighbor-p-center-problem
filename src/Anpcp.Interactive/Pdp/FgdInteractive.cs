using Anpcp.Core.Heuristics.Constructives;
using Anpcp.Core.Instances;
using Anpcp.Core.Solutions;
using Anpcp.Interactive.Pdp.Models;

using ScottPlot;
using ScottPlot.Plottables;

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

        var plotter = new Plot
        {
            ScaleFactor = PlotConfig.ScaleFactor
        };
        plotter.HideAxesAndGrid();

        // closed facilities
        var cfVertices = Instance.Facilities
            .Where(f => Solution.ClosedFacilities.Contains(f.Index));
        var cfMarkers = plotter.Add.Markers(
            cfVertices.Select(v => (double)v.XCoord).ToArray(),
            cfVertices.Select(v => (double)v.YCoord).ToArray());
        SetScatterProps(ref cfMarkers, PlotConfig.CfColor);

        // centers
        var sVertices = Instance.Facilities
            .Where(f => Solution.OpenFacilities.Contains(f.Index)
                && f.Index != LastInserted);
        var sMarkers = plotter.Add.Markers(
            sVertices.Select(v => (double)v.XCoord).ToArray(),
            sVertices.Select(v => (double)v.YCoord).ToArray());
        SetScatterProps(ref sMarkers, PlotConfig.SColor);

        var fiVertex = Instance.Facilities[fi];
        var fiCoords = new Coordinates(fiVertex.XCoord, fiVertex.YCoord);

        var liVertex = Instance.Facilities[LastInserted];
        var liCoords = new Coordinates(liVertex.XCoord, liVertex.YCoord);

        var ccVertex = Instance.Facilities[closestCenter.Index];
        var ccCoords = new Coordinates(ccVertex.XCoord, ccVertex.YCoord);

        var liLine = plotter.Add.Line(fiCoords, liCoords);
        liLine.LinePattern = LinePattern.Dotted;
        liLine.Color = new(ColorName.Black);

        var ccLine = plotter.Add.Line(fiCoords, ccCoords);
        ccLine.LinePattern = LinePattern.Dotted;
        ccLine.Color = new(ColorName.Black);

        var minLine = minDistance == liDistance
            ? liLine
            : ccLine;
        minLine.Color = new(ColorName.Goldenrod);

        var fiMarker = plotter.Add.Markers(
            (Coordinates[])[fiCoords]);
        SetScatterProps(ref fiMarker, PlotConfig.FiColor);

        var liMarker = plotter.Add.Markers(
            (Coordinates[])[liCoords]);
        SetScatterProps(ref liMarker, PlotConfig.LiColor);

        var ccMarker = plotter.Add.Markers(
            (Coordinates[])[ccCoords]);
        SetScatterProps(ref ccMarker, PlotConfig.CcColor);

        return plotter;
    }

    private void SetScatterProps(ref Markers markers, ColorName fillColor)
    {
        markers.MarkerStyle.OutlineWidth = PlotConfig.MarkerOutlineWidth;
        markers.MarkerStyle.OutlineColor = new(ColorName.Black);
        markers.MarkerStyle.FillColor = new(fillColor);
        markers.MarkerStyle.Size = PlotConfig.MarkerSize;
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