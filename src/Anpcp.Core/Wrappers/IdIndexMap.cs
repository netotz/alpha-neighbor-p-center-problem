using System.Collections.ObjectModel;

namespace Anpcp.Core.Wrappers;

public class IdIndexMap(
    Dictionary<int, int> usersDictionary,
    Dictionary<int, int> facilityDictionary)
{
    /// <summary>
    /// Maps user IDs to their indices in the matrix.
    /// </summary>
    public ReadOnlyDictionary<int, int> Users { get; } = new(usersDictionary);
    /// <summary>
    /// Maps facility IDs to their indices in the matrix.
    /// </summary>
    public ReadOnlyDictionary<int, int> Facilities { get; } = new(facilityDictionary);
}
