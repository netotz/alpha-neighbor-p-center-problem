using Anpcp.Core.Models;
using Anpcp.Core.Models.Enums;

namespace Anpcp.Core.IO;

/// <summary>
/// Reader for TSPLIB files.
/// </summary>
/// <remarks>
/// Currently supports files that specify <c>NODE_COORDS_SECTION</c> only.
/// </remarks>
public static class TspFileIO
{
    private static string NodeCoordSection { get; } = "NODE_COORD_SECTION";
    private static string Eof { get; } = "EOF";

    public static List<Vertex> ReadNodes(string filePath)
    {
        using var streamReader = new StreamReader(filePath);

        while (!streamReader.ReadLine()?.Contains(NodeCoordSection) ?? true) ;
        // all the next lines should be node coords

        var vertices = new List<Vertex>();

        var line = streamReader.ReadLine() ?? "";
        while (line != Eof)
        {
            line.Trim();

            // each line has format "i x y t?"
            var items = line.Split();
            var parsedItems = items.Select(int.Parse).ToArray();

            var type = VertexType.Both;
            // if file includes vertex type
            if (parsedItems.Length == 4)
            {
                type = (VertexType)parsedItems[3];
            }

            vertices.Add(
                new(parsedItems[0], parsedItems[1], parsedItems[2], type));

            line = streamReader.ReadLine() ?? "";
        }

        return vertices;
    }
}
