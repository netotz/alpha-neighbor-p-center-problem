namespace Anpcp.Core.Solutions.Models;

/// <summary>
/// Model for a user-facility allocation.
/// </summary>
public record Allocation(
    // TODO: validate default values
    int UserId = -1,
    int CenterId = -1,
    int Distance = -1);
