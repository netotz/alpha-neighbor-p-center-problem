namespace Anpcp.Interactive.Pdp.Models;

/// <summary>
/// Distance from fi to the closest center from S.
/// Type meant as the value of distances memory dictionary.
/// </summary>
public record ClosestCenter(int Distance, int Index = -1);