namespace Anpcp.Interactive.Pdp.Models;

/// <summary>
/// Configuration options passed to ScottPlot objects.
/// </summary>
public record PlotConfig
{
    public double ScaleFactor { get; init; } = 1;
    public float MarkerSize { get; init; } = 1;
    public float MarkerOutlineWidth { get; init; } = 1;
    /// <summary>
    /// Color for closed facilities markers.
    /// </summary>
    public ColorName CfColor { get; init; } = ColorName.Gray;
    /// <summary>
    /// Color for solution markers.
    /// </summary>
    public ColorName SColor { get; init; } = ColorName.Red;
    /// <summary>
    /// Color for facility to insert (fi) marker.
    /// </summary>
    public ColorName FiColor { get; init; } = ColorName.Yellow;
    /// <summary>
    /// Color for last inserted (li) facility marker.
    /// </summary>
    public ColorName LiColor { get; init; } = ColorName.Blue;
    /// <summary>
    /// Color for closest center (cc) marker to fi.
    /// </summary>
    public ColorName CcColor { get; init; } = ColorName.Green;
}

