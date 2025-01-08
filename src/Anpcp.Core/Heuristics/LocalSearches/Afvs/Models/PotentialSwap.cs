namespace Anpcp.Core.Heuristics.LocalSearches.Afvs.Models;

/// <summary>
///  Wraps the proposed facility to insert, the best facility to remove,
///  and the resulting x(S) of their swap found by <see cref="AlphaFastVertexSubstitution"/>.
/// </summary>
public record PotentialSwap(
    int FacilityIn,
    int FacilityOut,
    int ObjectiveFunctionValue);
