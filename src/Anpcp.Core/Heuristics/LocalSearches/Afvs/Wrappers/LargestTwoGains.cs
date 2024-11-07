using Anpcp.Core.Heuristics.LocalSearches.Afvs.Models;

namespace Anpcp.Core.Heuristics.LocalSearches.Afvs.Wrappers;

/// <summary>
/// Wraps the largest 2 gains from r(.)
/// </summary>
public class LargestTwoGains
{
    public GainsFacility First { get; private set; } = new(-1, -1);
    public GainsFacility Second { get; private set; } = new(-1, -1);

    public LargestTwoGains(Dictionary<int, int> gainsNeighbors)
    {
        // O(p)
        foreach (var (facilityId, objectiveFunctionValue) in gainsNeighbors)
        {
            TryUpdate(facilityId, objectiveFunctionValue);
        }
    }

    private bool TryUpdate(int facilityId, int objectiveFunctionValue)
    {
        var didUpdate = false;

        if (objectiveFunctionValue > First.ObjectiveFunctionValue)
        {
            Second = First;
            First = new(facilityId, objectiveFunctionValue);
            didUpdate = true;
        }
        else if (objectiveFunctionValue > Second.ObjectiveFunctionValue)
        {
            Second = new(facilityId, objectiveFunctionValue);
            didUpdate = true;
        }

        return didUpdate;
    }
}
