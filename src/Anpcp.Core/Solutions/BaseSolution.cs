using Anpcp.Core.Wrappers;

namespace Anpcp.Core.Solutions;

public abstract class BaseSolution(HashSet<int> closedFacilities)
{
    public int ObjectiveFunctionValue { get; set; }
    public HashSet<int> OpenFacilities { get; } = [];
    public HashSet<int> ClosedFacilities { get; } = closedFacilities;
    /// <summary>
    /// Indices pair of critical vertices whose distance
    /// defines <see cref="ObjectiveFunctionValue"/>.
    /// </summary>
    public (int, int) CriticalPair { get; protected set; } = (-1, -1);

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

    /// <summary>
    /// Updates property <see cref="ObjectiveFunctionValue"/>
    /// and returns it.
    /// </summary>
    public abstract int UpdateObjectiveFunctionValue(DistancesMatrix distances);
}
