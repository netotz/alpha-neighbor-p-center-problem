namespace Anpcp.Core;

public abstract class BaseSolution(HashSet<int> closedFacilities)
{
    public int ObjectiveFunctionValue { get; set; }
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

    /// <summary>
    /// Updates property <see cref="ObjectiveFunctionValue"/>
    /// and returns it.
    /// </summary>
    public abstract int UpdateObjectiveFunctionValue(Instance instance);
}
