import java.util.Scanner;

public class j1 {

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        if (!sc.hasNextInt())
            return;

        int n = sc.nextInt();
        int[] arr = new int[n];

        for (int i = 0; i < n; i++) {
            arr[i] = sc.nextInt();
        }

        for (int i = 2; i < n; i += 2) {
            int key = arr[i];
            int j = i - 2;

            while (j >= 0 && arr[j] < key) {
                arr[j + 2] = arr[j];
                j -= 2;
            }
            arr[j + 2] = key;
        }

        for (int i = 3; i < n; i += 2) {
            int key = arr[i];
            int j = i - 2;

            while (j >= 0 && arr[j] > key) {
                arr[j + 2] = arr[j];
                j -= 2;
            }
            arr[j + 2] = key;
        }

        // 3. Print the formatted output
        for (int i = 0; i < n; i++) {
            System.out.print(arr[i]);
            if (i < n - 1) {
                System.out.print(" ");
            }
        }
        System.out.println();

        sc.close();
    }
}