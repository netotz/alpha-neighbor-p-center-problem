using Anpcp.Core.IO;

namespace Anpcp.Core;

/// <summary>
/// An instance of the ANPCP with one set of nodes for both users and facilities.
/// </summary>
public class InstanceSameSet : Instance
{
    /// <summary>
    /// Creates an instance from a TSPLIB file.
    /// </summary>
    /// <remarks>
    /// The extension must be <c>*.tsp</c>
    /// </remarks>
    public InstanceSameSet(string tspFilePath)
    {
        var vertices = TspFileIO.ReadNodes(tspFilePath).ToArray();

        Facilities = vertices;
        Users = vertices;

        InitDistancesMatrices();
    }
}
