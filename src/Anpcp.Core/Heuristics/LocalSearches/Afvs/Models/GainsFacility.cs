namespace Anpcp.Core.Heuristics.LocalSearches.Afvs.Models;

/// <summary>
/// Wrapper of a facility from r(.) that contributes gains to the objective function value.
/// </summary>
public record GainsFacility(
    // TODO: validate default values
    int Id,
    int ObjectiveFunctionValue);
