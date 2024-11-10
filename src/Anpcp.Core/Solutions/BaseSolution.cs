using Anpcp.Core.Solutions.Models;

namespace Anpcp.Core.Solutions;

public abstract class BaseSolution(HashSet<int> closedFacilities)
{
    public Allocation CriticalAllocation { get; protected set; } = new();
    public int ObjectiveFunctionValue => CriticalAllocation.Distance;
    public HashSet<int> OpenFacilities { get; } = [];
    public HashSet<int> ClosedFacilities { get; } = closedFacilities;

    public void Insert(int facilityId)
    {
        ClosedFacilities.Remove(facilityId);
        OpenFacilities.Add(facilityId);
    }

    public void Remove(int facilityId)
    {
        OpenFacilities.Remove(facilityId);
        ClosedFacilities.Add(facilityId);
    }

    public void Swap(int facilityInId, int facilityOutId)
    {
        Insert(facilityInId);
        Remove(facilityOutId);
    }
}
