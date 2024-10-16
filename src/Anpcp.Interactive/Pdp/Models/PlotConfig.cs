namespace Anpcp.Interactive.Pdp.Models;

/// <summary>
/// Configuration options passed to ScottPlot objects.
/// </summary>
public record PlotConfig
{
    public double ScaleFactor { get; init; } = 2;
    public float MarkerSize { get; init; } = 10;
    public float MarkerOutlineWidth { get; init; } = 0.7f;
    /// <summary>
    /// Color for closed facilities markers.
    /// </summary>
    public ColorName CfColor { get; init; } = ColorName.LightGray;
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
    public ColorName LiColor { get; init; } = ColorName.Red;
    /// <summary>
    /// Color for closest center (cc) marker to fi.
    /// </summary>
    public ColorName CcColor { get; init; } = ColorName.Red;
}

