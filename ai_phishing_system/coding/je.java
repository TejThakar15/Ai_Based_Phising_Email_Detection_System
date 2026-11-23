import java.util.*;

public class je {
    public static void main(String args[]) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();
        int[] arr = new int[n];
        for (int i = 0; i < n; i++) {
            arr[i] = sc.nextInt();
        }

        HashSet<Integer> visited = new HashSet<>();
        int firstRepeated = -1;
        boolean found = false;
        for (int i = n - 1; i >= 0; i--) {
            if (visited.contains(arr[i])) {
                firstRepeated = arr[i];
                found = true;
            } else {
                visited.add(arr[i]);
            }

        }
        if (found) {
            System.out.println(firstRepeated);
        } else {
            System.out.println("No Repeated elenebt found in the array");
        }

    }
}