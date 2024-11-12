using Anpcp.Core.Solutions.Models;

namespace Anpcp.Core.Solutions;

public abstract class BaseSolution
{
    public Allocation CriticalAllocation { get; protected set; } = new();
    public int ObjectiveFunctionValue => CriticalAllocation.Distance;
    public HashSet<int> Centers { get; }
    public int Size => Centers.Count;
    public HashSet<int> ClosedFacilities { get; }

    /// <summary>
    /// Constructs an empty solution with no centers and
    /// <paramref name="allFacilities"/> as closed facilities.
    /// </summary>
    public BaseSolution(HashSet<int> allFacilities)
    {
        ClosedFacilities = allFacilities;
        Centers = [];
    }

    /// <summary>
    /// Constructs a specific solution.
    /// This does not guarantee feasibility nor a correct <see cref="CriticalAllocation"/>.
    /// </summary>
    public BaseSolution(
        HashSet<int> closedFacilities,
        HashSet<int> openFacilities,
        Allocation criticalAllocation)
    {
        CriticalAllocation = criticalAllocation;
        ClosedFacilities = closedFacilities;
        Centers = openFacilities;
    }

    /// <summary>
    /// Constructs a copy of <paramref name="originalSolution"/> to avoid cross references.
    /// </summary>
    /// <remarks>Time O(m)</remarks>
    public BaseSolution(BaseSolution originalSolution)
    {
        CriticalAllocation = new(
            originalSolution.CriticalAllocation.UserId,
            originalSolution.CriticalAllocation.CenterId,
            originalSolution.CriticalAllocation.Distance);
        // O(m)
        ClosedFacilities = [.. originalSolution.ClosedFacilities];
        // O(p)
        Centers = [.. originalSolution.Centers];
    }

    public void Insert(int facilityId)
    {
        ClosedFacilities.Remove(facilityId);
        Centers.Add(facilityId);
    }

    public void Remove(int facilityId)
    {
        Centers.Remove(facilityId);
        ClosedFacilities.Add(facilityId);
    }

    public void Swap(int facilityInId, int facilityOutId)
    {
        Insert(facilityInId);
        Remove(facilityOutId);
    }
}
