using Anpcp.Core.Heuristics.Constructives;
using Anpcp.Core.Instances;
using Anpcp.Core.Solutions;
using Anpcp.Interactive.Pdp.Models;

using ScottPlot;
using ScottPlot.Plottables;

namespace Anpcp.Interactive.Pdp;

/// <summary>
/// Interactive version of <see cref="FastGreedyDispersion"/> to generate visualizations.
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
    public Queue<int> ClosedFacilitiesQueue { get; private set; }
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
    }

    private void Start()
    {
        // start solution with 2 farthest facilities
        var f1 = Instance.DistancesFF.MaxPair.Item1;
        var f2 = Instance.DistancesFF.MaxPair.Item2;

        foreach (var f in (int[])[f1, f2])
        {
            LastInserted = f;
            Solution.Insert(f);
            DistancesMemory.Remove(LastInserted);

            Solution.UpdateObjectiveFunctionValue(Instance.DistancesFF);

            ResetClosedFacilitiesQueue();
            HurryForMemory();
        }
    }

    public void ResetClosedFacilitiesQueue()
    {
        ClosedFacilitiesQueue = new Queue<int>(Solution.ClosedFacilities);
    }

    /// <summary>
    /// Tries to do an iteration of the main `while` loop of the algorithm.
    /// </summary>
    /// <returns>`false` if |S| = p or memory isn't fully updated</returns>
    public Plot? TryPlotMainIteration(string savePath = "")
    {
        // S already has p centers
        if (Solution.OpenFacilities.Count == PSize)
        {
            return null;
        }

        // if memory isn't fully updated
        if (ClosedFacilitiesQueue.Count > 0)
        {
            return null;
        }

        // get farthest facility to S
        // O(m - p) ~= O(m)
        LastInserted = DistancesMemory
            .MaxBy(p => p.Value.Distance)
            .Key;

        var closestCenter = DistancesMemory[LastInserted];

        var prevOfv = CurrentOfv;
        var prevCriticalPair = Solution.CriticalPair;

        Solution.Insert(LastInserted);

        // update x(S)
        CurrentOfv = Math.Min(
            CurrentOfv,
            closestCenter.Distance);
        Solution.UpdateObjectiveFunctionValue(Instance.DistancesFF);

        var memoryPrinted = string.Join(
            ", ",
            DistancesMemory.Select(p => $"{p.Key}: {p.Value.Distance}"));
        Console.WriteLine($"{{{memoryPrinted}}}");

        DistancesMemory.Remove(LastInserted);

        ResetClosedFacilitiesQueue();

        var plotter = GetCommonPlotter();

        // critical pairs
        var cp1Vertex = Instance.Facilities[prevCriticalPair.Item1];
        var cp1Coords = new Coordinates(cp1Vertex.XCoord, cp1Vertex.YCoord);

        var cp2Vertex = Instance.Facilities[prevCriticalPair.Item2];
        var cp2Coords = new Coordinates(cp2Vertex.XCoord, cp2Vertex.YCoord);

        var cpLine = plotter.Add.Line(cp1Coords, cp2Coords);
        cpLine.LinePattern = LinePattern.Dotted;
        cpLine.Color = new(ColorName.Black);

        var liVertex = Instance.Facilities[LastInserted];
        var liCoords = new Coordinates(liVertex.XCoord, liVertex.YCoord);

        var ccVertex = Instance.Facilities[closestCenter.Index];
        var ccCoords = new Coordinates(ccVertex.XCoord, ccVertex.YCoord);

        var liLine = plotter.Add.Line(liCoords, ccCoords);
        liLine.LinePattern = LinePattern.Dotted;
        liLine.Color = new(ColorName.Black);

        var minLine = prevOfv == CurrentOfv
            ? cpLine
            : liLine;
        minLine.Color = new(ColorName.Goldenrod);

        var liMarker = plotter.Add.Markers(
            (Coordinates[])[liCoords]);
        liMarker.LegendText = "Last inserted";
        SetScatterProps(ref liMarker, PlotConfig.LiColor, MarkerShape.FilledTriangleDown);

        var ccMarker = plotter.Add.Markers(
            (Coordinates[])[ccCoords]);
        ccMarker.LegendText = "Nearest center";
        SetScatterProps(ref ccMarker, PlotConfig.CcColor, MarkerShape.FilledSquare);

        if (!string.IsNullOrEmpty(savePath))
        {
            plotter.ScaleFactor = 5;
            plotter.SavePng(savePath, 2000, 1250);
            plotter.ScaleFactor = PlotConfig.ScaleFactor;
        }

        return plotter;
    }

    /// <summary>
    /// Tries to plot an iteration of the `for` loop that updates the memory.
    /// </summary>
    /// <returns>`null` if memory is completely updated.</returns>
    public Plot? TryPlotForMemoryIteration(
        bool isHurrying = false,
        string savePath = "")
    {
        // if empty
        if (!ClosedFacilitiesQueue.TryDequeue(out var fi))
        {
            return null;
        }

        var closestCenter = DistancesMemory[fi];
        var liDistance = Instance.DistancesFF[fi, LastInserted];
        var minDistance = Math.Min(closestCenter.Distance, liDistance);

        var memoryPrinted = string.Join(
            ", ",
            DistancesMemory.Select(p => $"{p.Key}: {p.Value.Distance}"));
        Console.WriteLine($"{{{memoryPrinted}}}");

        // only update if necessary (li < cc)
        if (minDistance == liDistance)
        {
            Console.WriteLine("min: li");
            DistancesMemory[fi] = new(minDistance, LastInserted);
        }

        if (isHurrying)
        {
            return null;
        }

        var plotter = GetCommonPlotter();

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
        fiMarker.LegendText = $"Candidate facility, i={fi}";
        SetScatterProps(ref fiMarker, PlotConfig.FiColor);

        var liMarker = plotter.Add.Markers(
            (Coordinates[])[liCoords]);
        liMarker.LegendText = "Last inserted";
        SetScatterProps(ref liMarker, PlotConfig.LiColor, MarkerShape.FilledTriangleDown);

        var ccMarker = plotter.Add.Markers(
            (Coordinates[])[ccCoords]);
        ccMarker.LegendText = "Nearest center";
        SetScatterProps(ref ccMarker, PlotConfig.CcColor, MarkerShape.FilledSquare);

        if (!string.IsNullOrEmpty(savePath))
        {
            plotter.ScaleFactor = 5;
            plotter.SavePng(savePath, 2000, 1250);
            plotter.ScaleFactor = PlotConfig.ScaleFactor;
        }

        return plotter;
    }

    private Plot GetCommonPlotter()
    {
        var plotter = new Plot
        {
            ScaleFactor = PlotConfig.ScaleFactor
        };
        plotter.HideAxesAndGrid();
        plotter.ShowLegend(Edge.Bottom);
        plotter.Legend.Orientation = Orientation.Horizontal;
        plotter.Legend.FontSize = PlotConfig.LegendFontSize;

        // closed facilities
        var cfVertices = Instance.Facilities
            .Where(f => Solution.ClosedFacilities.Contains(f.Index));
        var cfMarkers = plotter.Add.Markers(
            cfVertices.Select(v => (double)v.XCoord).ToArray(),
            cfVertices.Select(v => (double)v.YCoord).ToArray());
        cfMarkers.LegendText = "Closed facilities";
        SetScatterProps(ref cfMarkers, PlotConfig.CfColor);

        // centers
        var sVertices = Instance.Facilities
            .Where(f => Solution.OpenFacilities.Contains(f.Index)
                && f.Index != LastInserted);
        var sMarkers = plotter.Add.Markers(
            sVertices.Select(v => (double)v.XCoord).ToArray(),
            sVertices.Select(v => (double)v.YCoord).ToArray());
        sMarkers.LegendText = "Other centers";
        SetScatterProps(ref sMarkers, PlotConfig.SColor);

        return plotter;
    }

    private void SetScatterProps(
        ref Markers markers,
        ColorName fillColor,
        MarkerShape shape = MarkerShape.FilledCircle)
    {
        markers.MarkerStyle.Shape = shape;
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