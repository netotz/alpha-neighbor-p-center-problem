namespace Anpcp.Interactive.Pdp.Models;

/// <summary>
/// Configuration options passed to ScottPlot objects.
/// </summary>
public record PlotConfig
{
    public double ScaleFactor { get; init; } = 1;
    public float MarkerSize { get; init; } = 1;
    public float MarkerLineWidth { get; init; } = 1;
    public ColorName CfColor { get; init; } = ColorName.Gray;
    public ColorName SColor { get; init; } = ColorName.Red;
    public ColorName FiColor { get; init; } = ColorName.Yellow;
    public ColorName LiColor { get; init; } = ColorName.Blue;
    public ColorName CcColor { get; init; } = ColorName.Green;
}

