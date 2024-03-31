using Anpcp.Core.Enums;
using Anpcp.Core.Models;

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

            // each line has format "i x y t"
            var items = line.Split();
            var parsedItems = items.Select(int.Parse).ToArray();

            vertices.Add(
                new(parsedItems[0], parsedItems[1], parsedItems[2], (VertexType)parsedItems[3]));

            line = streamReader.ReadLine() ?? "";
        }

        return vertices;
    }
}
