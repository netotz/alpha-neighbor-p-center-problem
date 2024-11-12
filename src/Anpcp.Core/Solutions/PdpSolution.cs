using Anpcp.Core.Wrappers;

namespace Anpcp.Core.Solutions;

public class PdpSolution(HashSet<int> closedFacilities)
    : BaseSolution(closedFacilities)
{
    /// <summary>
    /// Finds the minimum distance among all pairs of centers,
    /// updates <see cref="BaseSolution.CriticalAllocation"/> and returns x(S).
    /// </summary>
    /// <param name="distancesFF">Distances matrix of facilities.</param>
    /// <remarks>Time O(p**2)</remarks>
    public int UpdateCriticalAllocation(DistancesMatrix distancesFF)
    {
        // O(p)
        var openFacilitiesArray = Centers.ToArray();

        var minDistance = int.MaxValue;

        //// O(p**2)
        // O(p)
        for (var i = 0; i < openFacilitiesArray.Length; i++)
        {
            var center1 = openFacilitiesArray[i];
            // O(p)
            for (var j = i + 1; j < openFacilitiesArray.Length; j++)
            {
                var center2 = openFacilitiesArray[j];

                var distance = distancesFF[center1, center2];

                if (distance < minDistance)
                {
                    minDistance = distance;
                    CriticalAllocation = new(center1, center2, minDistance);
                }
            }
        }

        return ObjectiveFunctionValue;
    }

    /// <summary>
    /// Updates the critical allocation by just creating a new object, without calculations.
    /// </summary>
    /// <returns>
    /// <paramref name="distance"/> which is the new <see cref="BaseSolution.ObjectiveFunctionValue"/>.
    /// </returns>
    public int UpdateCriticalAllocation(int center1, int center2, int distance)
    {
        CriticalAllocation = new(center1, center2, distance);

        return ObjectiveFunctionValue;
    }
}
